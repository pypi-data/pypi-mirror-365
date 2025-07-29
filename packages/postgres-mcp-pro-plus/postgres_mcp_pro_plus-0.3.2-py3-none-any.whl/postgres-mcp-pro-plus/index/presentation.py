"""Database Tuning Advisor (DTA) tool for Postgres MCP."""

import logging
import os
from typing import Any
from typing import Dict
from typing import List

import humanize

from ..artifacts import ExplainPlanArtifact
from ..artifacts import calculate_improvement_multiple
from ..sql import SqlDriver
from .dta_calc import IndexTuningBase
from .index_opt_base import IndexDefinition
from .index_opt_base import IndexTuningResult

logger = logging.getLogger(__name__)


class TextPresentation:
    """Text-based presentation of index tuning recommendations."""

    def __init__(self, sql_driver: SqlDriver, index_tuning: IndexTuningBase):
        """
        Initialize the presentation.

        Args:
            conn: The PostgreSQL connection object
        """
        self.sql_driver = sql_driver
        self.index_tuning = index_tuning

    async def analyze_workload(self, max_index_size_mb=10000):
        """
        Analyze SQL workload and recommend indexes.

        This method analyzes queries from database query history, examining
        frequently executed and costly queries to recommend the most beneficial indexes.

        Args:
            max_index_size_mb: Maximum total size for recommended indexes in MB

        Returns:
            String with recommendations or error
        """
        result = await self._execute_analysis(
            min_calls=50,
            min_avg_time_ms=5.0,
            limit=100,
            max_index_size_mb=max_index_size_mb,
        )
        return self._format_as_text(result)

    async def analyze_queries(self, queries, max_index_size_mb=10000):
        """
        Analyze a list of SQL queries and recommend indexes.

        This method examines the provided SQL queries and recommends
        indexes that would improve their performance.

        Args:
            queries: List of SQL queries to analyze
            max_index_size_mb: Maximum total size for recommended indexes in MB

        Returns:
            String with recommendations or error
        """
        if not queries:
            return "❌ Error: No queries provided for analysis"

        result = await self._execute_analysis(
            query_list=queries,
            min_calls=0,  # Ignore min calls for explicit query list
            min_avg_time_ms=0,  # Ignore min time for explicit query list
            limit=0,  # Ignore limit for explicit query list
            max_index_size_mb=max_index_size_mb,
        )
        return self._format_as_text(result)

    async def analyze_single_query(self, query, max_index_size_mb=10000):
        """
        Analyze a single SQL query and recommend indexes.

        This method examines the provided SQL query and recommends
        indexes that would improve its performance.

        Args:
            query: SQL query to analyze
            max_index_size_mb: Maximum total size for recommended indexes in MB

        Returns:
            String with recommendations or error
        """
        result = await self._execute_analysis(
            query_list=[query],
            min_calls=0,  # Ignore min calls for explicit query
            min_avg_time_ms=0,  # Ignore min time for explicit query
            limit=0,  # Ignore limit for explicit query
            max_index_size_mb=max_index_size_mb,
        )
        return self._format_as_text(result)

    async def _execute_analysis(
        self,
        query_list=None,
        min_calls=50,
        min_avg_time_ms=5.0,
        limit=100,
        max_index_size_mb=10000,
    ):
        """
        Execute indexing analysis

        Returns:
            Dict with recommendations or dict with error
        """
        try:
            # Run the index tuning analysis
            session = await self.index_tuning.analyze_workload(
                query_list=query_list,
                min_calls=min_calls,
                min_avg_time_ms=min_avg_time_ms,
                limit=limit,
                max_index_size_mb=max_index_size_mb,
            )

            # Prepare the response to send back to the caller
            include_langfuse_trace = os.environ.get("POSTGRES_MCP_INCLUDE_LANGFUSE_TRACE", "true").lower() == "true"
            langfuse_trace = {"_langfuse_trace": session.dta_traces} if include_langfuse_trace else {}

            if session.error:
                return {
                    "error": session.error,
                    **langfuse_trace,
                }

            if not session.recommendations:
                return {
                    "recommendations": "No index recommendations found.",
                    **langfuse_trace,
                }

            # Calculate overall statistics
            total_size_bytes = sum(rec.estimated_size_bytes for rec in session.recommendations)

            # Calculate overall performance improvement
            initial_cost = session.recommendations[0].progressive_base_cost if session.recommendations else 0
            new_cost = session.recommendations[-1].progressive_recommendation_cost if session.recommendations else 1.0
            improvement_multiple = calculate_improvement_multiple(initial_cost, new_cost)

            # Build recommendations list
            recommendations = self._build_recommendations_list(session)

            # Generate query impact section using helper function
            query_impact = await self._generate_query_impact(session)

            # Create the result JSON object with summary, recommendations, and query impact
            return {
                "summary": {
                    "total_recommendations": len(session.recommendations),
                    "base_cost": f"{initial_cost:.1f}",
                    "new_cost": f"{new_cost:.1f}",
                    "total_size_bytes": humanize.naturalsize(total_size_bytes),
                    "improvement_multiple": f"{improvement_multiple:.1f}",
                },
                "recommendations": recommendations,
                "query_impact": query_impact,
                **langfuse_trace,
            }
        except Exception as e:
            logger.error(f"Error analyzing queries: {e}", exc_info=True)
            return {"error": f"Error analyzing queries: {e}"}

    def _build_recommendations_list(self, session: IndexTuningResult) -> List[Dict[str, Any]]:
        recommendations = []
        for index_apply_order, rec in enumerate(session.recommendations):
            rec_dict = {
                "index_apply_order": index_apply_order + 1,
                "index_target_table": rec.table,
                "index_target_columns": rec.columns,
                "benefit_of_this_index_only": {
                    "improvement_multiple": f"{rec.individual_improvement_multiple:.1f}",
                    "base_cost": f"{rec.individual_base_cost:.1f}",
                    "new_cost": f"{rec.individual_recommendation_cost:.1f}",
                },
                "benefit_after_previous_indexes": {
                    "improvement_multiple": f"{rec.progressive_improvement_multiple:.1f}",
                    "base_cost": f"{rec.progressive_base_cost:.1f}",
                    "new_cost": f"{rec.progressive_recommendation_cost:.1f}",
                },
                "index_estimated_size": humanize.naturalsize(rec.estimated_size_bytes),
                "index_definition": rec.definition,
            }
            if rec.potential_problematic_reason == "long_text_column":
                rec_dict["warning"] = (
                    "This index is potentially problematic because it includes a long text column. "
                    "You might not be able to create this index if the index row size becomes too large "
                    "(i.e., more than 8191 bytes)."
                )
            elif rec.potential_problematic_reason:
                rec_dict["warning"] = (
                    f"This index is potentially problematic because it includes a {rec.potential_problematic_reason} column."
                )
            recommendations.append(rec_dict)
        return recommendations

    async def _generate_query_impact(self, session: IndexTuningResult) -> List[Dict[str, Any]]:
        """
        Generate the query impact section showing before/after explain plans.

        Args:
            session: DTASession containing recommendations

        Returns:
            List of dictionaries with query and explain plans
        """
        query_impact = []

        # Get workload queries from the first recommendation
        # (All recommendations have the same queries)
        if not session.recommendations:
            return query_impact

        workload_queries = session.recommendations[0].queries

        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in workload_queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)

        # Get before and after plans for each query
        if unique_queries and self.index_tuning:
            for query in unique_queries:
                # Get plan with no indexes
                before_plan = await self.index_tuning.get_explain_plan_with_indexes(query, frozenset())

                # Get plan with all recommended indexes
                index_configs = frozenset(
                    IndexDefinition(rec.table, rec.columns, rec.using) for rec in session.recommendations
                )
                after_plan = await self.index_tuning.get_explain_plan_with_indexes(query, index_configs)

                # Extract costs from plans
                base_cost = self.index_tuning.extract_cost_from_json_plan(before_plan)
                new_cost = self.index_tuning.extract_cost_from_json_plan(after_plan)

                # Calculate improvement multiple
                improvement_multiple = "∞"  # Default for cases where new_cost is zero
                if new_cost > 0 and base_cost > 0:
                    improvement_multiple = f"{calculate_improvement_multiple(base_cost, new_cost):.1f}"

                before_plan_text = ExplainPlanArtifact.format_plan_summary(before_plan)
                after_plan_text = ExplainPlanArtifact.format_plan_summary(after_plan)
                diff_text = ExplainPlanArtifact.create_plan_diff(before_plan, after_plan)

                # Add to query impact with costs and improvement
                query_impact.append(
                    {
                        "query": query,
                        "base_cost": f"{base_cost:.1f}",
                        "new_cost": f"{new_cost:.1f}",
                        "improvement_multiple": improvement_multiple,
                        "before_explain_plan": "```\n" + before_plan_text + "\n```",
                        "after_explain_plan": "```\n" + after_plan_text + "\n```",
                        "explain_plan_diff": "```\n" + diff_text + "\n```",
                    }
                )

        return query_impact

    def _format_as_text(self, result: Dict[str, Any]) -> str:
        """Format index tuning analysis result as human-readable text."""
        if "error" in result:
            return f"❌ Error: {result['error']}"

        output = []

        # Header
        output.append("📊 INDEX TUNING ANALYSIS")
        output.append("=" * 50)

        # Summary
        summary = result.get("summary", {})
        if summary:
            output.append("📈 SUMMARY")
            output.append("-" * 30)
            output.append(f"Total Recommendations: {summary.get('total_recommendations', 0)}")
            output.append(f"Base Cost: {summary.get('base_cost', 'N/A')}")
            output.append(f"New Cost: {summary.get('new_cost', 'N/A')}")
            output.append(f"Performance Improvement: {summary.get('improvement_multiple', 'N/A')}x")
            output.append(f"Total Index Size: {summary.get('total_size_bytes', 'N/A')}")
            output.append("")

        # Recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            output.append("🎯 INDEX RECOMMENDATIONS")
            output.append("-" * 40)

            for i, rec in enumerate(recommendations, 1):
                output.append(f"{i}. INDEX ON {rec.get('index_target_table', 'unknown_table')}")
                output.append(f"   Columns: {', '.join(rec.get('index_target_columns', []))}")
                output.append(f"   Definition: {rec.get('index_definition', 'N/A')}")
                output.append(f"   Estimated Size: {rec.get('index_estimated_size', 'N/A')}")
                output.append(f"   Apply Order: {rec.get('index_apply_order', 'N/A')}")

                # Individual benefit
                individual_benefit = rec.get("benefit_of_this_index_only", {})
                if individual_benefit:
                    output.append(f"   Individual Benefit:")
                    output.append(f"     • Improvement: {individual_benefit.get('improvement_multiple', 'N/A')}x")
                    output.append(f"     • Base Cost: {individual_benefit.get('base_cost', 'N/A')}")
                    output.append(f"     • New Cost: {individual_benefit.get('new_cost', 'N/A')}")

                # Progressive benefit
                progressive_benefit = rec.get("benefit_after_previous_indexes", {})
                if progressive_benefit:
                    output.append(f"   Progressive Benefit (after previous indexes):")
                    output.append(f"     • Improvement: {progressive_benefit.get('improvement_multiple', 'N/A')}x")
                    output.append(f"     • Base Cost: {progressive_benefit.get('base_cost', 'N/A')}")
                    output.append(f"     • New Cost: {progressive_benefit.get('new_cost', 'N/A')}")

                # Warnings
                if "warning" in rec:
                    output.append(f"   ⚠️  Warning: {rec['warning']}")

                output.append("")

        # Query Impact
        query_impact = result.get("query_impact", [])
        if query_impact:
            output.append("🔍 QUERY IMPACT ANALYSIS")
            output.append("-" * 40)

            for i, impact in enumerate(query_impact, 1):
                output.append(f"{i}. QUERY ANALYSIS")
                output.append(f"   Performance Improvement: {impact.get('improvement_multiple', 'N/A')}x")
                output.append(f"   Base Cost: {impact.get('base_cost', 'N/A')}")
                output.append(f"   New Cost: {impact.get('new_cost', 'N/A')}")

                # Query (truncated for readability)
                query = impact.get("query", "")
                if query:
                    query_lines = query.strip().split("\n")
                    if len(query_lines) > 3:
                        query_preview = "\n".join(query_lines[:3]) + "\n..."
                    else:
                        query_preview = query
                    output.append(f"   Query Preview:")
                    output.append(f"   ```sql")
                    output.append(f"   {query_preview}")
                    output.append(f"   ```")

                # Explain plan diff (if available)
                if impact.get("explain_plan_diff"):
                    output.append(f"   Explain Plan Difference:")
                    output.append(f"   {impact['explain_plan_diff']}")

                output.append("")

        # No recommendations case
        if not recommendations:
            if "recommendations" in result and result["recommendations"] == "No index recommendations found.":
                output.append("ℹ️ ANALYSIS RESULT")
                output.append("-" * 30)
                output.append("No index recommendations found.")
                output.append("")
                output.append("This could mean:")
                output.append("• Your queries are already well-optimized")
                output.append("• Existing indexes are sufficient")
                output.append("• Query patterns don't benefit from additional indexes")
                output.append("• No queries met the minimum criteria for analysis")
                output.append("")
                output.append("💡 SUGGESTIONS")
                output.append("-" * 30)
                output.append("• Review your query patterns and frequency")
                output.append("• Consider lowering analysis thresholds")
                output.append("• Check if pg_stat_statements is enabled and has data")
                output.append("• Analyze specific problematic queries individually")

        # Performance Tips
        if recommendations:
            output.append("💡 IMPLEMENTATION TIPS")
            output.append("-" * 30)
            output.append("• Apply indexes in the recommended order")
            output.append("• Test indexes on a staging environment first")
            output.append("• Monitor index usage after creation")
            output.append("• Consider maintenance windows for large indexes")
            output.append("• Use CONCURRENTLY option for minimal downtime")
            output.append("")

            output.append("📋 EXAMPLE IMPLEMENTATION")
            output.append("-" * 30)
            for i, rec in enumerate(recommendations[:3], 1):  # Show first 3 examples
                output.append(f"{i}. {rec.get('index_definition', 'N/A')}")
            if len(recommendations) > 3:
                output.append(f"   ... and {len(recommendations) - 3} more indexes")

        return "\n".join(output)
