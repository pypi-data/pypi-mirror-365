"""
Report Controller - Specialized Controller for Report Generation Operations

This module provides a dedicated controller for report generation and analysis,
extracted from the main controller for better performance and modularity.
It handles scientific report generation, statistical analysis, and visualization
export operations.

Key Features:
- High-performance report generation
- Multiple output formats (HTML, PDF, Markdown, JSON)
- Statistical analysis integration
- Plot generation and embedding
- Memory-efficient large dataset handling
- Thread-safe report operations

Classes:
    ReportController: Main report generation controller
"""

import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ReportController:
    """
    Specialized controller for report generation in Bayesian optimization.
    
    This controller handles all aspects of report generation including
    data analysis, visualization creation, and multi-format export.
    """
    
    def __init__(self):
        """Initialize report controller."""
        self._report_cache = {}
        self._lock = threading.Lock()
        
        # Import report generators
        try:
            from ..utils.enhanced_report_generator import enhanced_report_generator
            self.enhanced_generator = enhanced_report_generator
        except ImportError:
            logger.warning("Enhanced report generator not available")
            self.enhanced_generator = None
        
        try:
            from ..utils.scientific_utilities import scientific_validator, report_generator
            self.scientific_validator = scientific_validator
            self.report_generator = report_generator
        except ImportError:
            logger.warning("Scientific utilities not available")
            self.scientific_validator = None
            self.report_generator = None
        
        logger.info("ReportController initialized")
    
    def generate_optimization_report(
        self,
        optimizer: Any,
        report_type: str = "comprehensive",
        output_format: str = "html",
        filepath: Union[str, Path] = None,
        plot_configs: Optional[Dict[str, Any]] = None,
        include_statistics: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive optimization report.
        
        Args:
            optimizer: The optimization engine instance
            report_type: Type of report ("comprehensive", "summary", "statistical")
            output_format: Output format ("html", "pdf", "markdown", "json")
            filepath: Path to save report (optional)
            plot_configs: Configuration for plots to include
            include_statistics: Whether to include statistical analysis
            
        Returns:
            Dictionary with report generation results
        """
        try:
            logger.info(f"Generating {report_type} report in {output_format} format")
            
            # Prepare base report data
            report_data = self._prepare_base_report_data(optimizer)
            
            # Add statistical analysis if requested
            if include_statistics and self.scientific_validator:
                stats_data = self._gather_statistical_analysis_data(optimizer)
                report_data.update(stats_data)
            
            # Add correlation analysis
            correlations = self._calculate_correlations(optimizer)
            report_data["correlations"] = correlations
            
            # Generate plots if plot manager is available
            plots_base64 = {}
            if plot_configs and hasattr(optimizer, 'plot_manager'):
                plots_base64 = self._generate_plot_images(optimizer, plot_configs)
            
            # Generate report using appropriate generator
            success = self._export_report_with_fallback(
                report_type, report_data, output_format, filepath, plots_base64
            )
            
            result = {
                "success": success,
                "report_type": report_type,
                "output_format": output_format,
                "filepath": str(filepath) if filepath else None,
                "data_points": report_data.get("total_experiments", 0),
                "plots_included": len(plots_base64)
            }
            
            if success:
                logger.info(f"Report generated successfully: {filepath}")
            else:
                logger.error("Report generation failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating optimization report: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "report_type": report_type,
                "output_format": output_format
            }
    
    def generate_pareto_analysis_report(
        self,
        optimizer: Any,
        output_format: str = "html",
        filepath: Union[str, Path] = None
    ) -> Dict[str, Any]:
        """
        Generate specialized Pareto front analysis report.
        
        Args:
            optimizer: The optimization engine instance
            output_format: Output format
            filepath: Path to save report
            
        Returns:
            Dictionary with report generation results
        """
        try:
            logger.info("Generating Pareto analysis report")
            
            # Get Pareto front data
            pareto_X, pareto_obj, pareto_indices = optimizer.get_pareto_front()
            
            if pareto_X.empty or pareto_obj.empty:
                logger.warning("No Pareto front data available")
                return {"success": False, "error": "No Pareto front data available"}
            
            # Prepare Pareto-specific report data
            report_data = {
                "report_title": "Pareto Front Analysis",
                "timestamp": datetime.now().isoformat(),
                "pareto_points": len(pareto_indices),
                "total_experiments": len(getattr(optimizer, 'experimental_data', pd.DataFrame())),
                "objectives": getattr(optimizer, 'objective_names', []),
                "pareto_efficiency": len(pareto_indices) / len(getattr(optimizer, 'experimental_data', pd.DataFrame())) if hasattr(optimizer, 'experimental_data') and not optimizer.experimental_data.empty else 0,
                "pareto_solutions": pareto_obj.to_dict("records"),
                "pareto_parameters": pareto_X.to_dict("records"),
                "hypervolume": optimizer._calculate_hypervolume_legacy() if hasattr(optimizer, '_calculate_hypervolume_legacy') else 0.0
            }
            
            # Add Pareto front statistics
            if not pareto_obj.empty:
                pareto_stats = {}
                for obj_name in pareto_obj.columns:
                    obj_data = pareto_obj[obj_name]
                    pareto_stats[obj_name] = {
                        "min": float(obj_data.min()),
                        "max": float(obj_data.max()),
                        "mean": float(obj_data.mean()),
                        "std": float(obj_data.std()),
                        "range": float(obj_data.max() - obj_data.min())
                    }
                report_data["pareto_statistics"] = pareto_stats
            
            # Generate report
            success = self._export_report_with_fallback(
                "pareto_analysis", report_data, output_format, filepath
            )
            
            return {
                "success": success,
                "report_type": "pareto_analysis",
                "pareto_points": len(pareto_indices),
                "filepath": str(filepath) if filepath else None
            }
            
        except Exception as e:
            logger.error(f"Error generating Pareto analysis report: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def generate_convergence_report(
        self,
        optimizer: Any,
        output_format: str = "html",
        filepath: Union[str, Path] = None
    ) -> Dict[str, Any]:
        """
        Generate convergence analysis report.
        
        Args:
            optimizer: The optimization engine instance
            output_format: Output format
            filepath: Path to save report
            
        Returns:
            Dictionary with report generation results
        """
        try:
            logger.info("Generating convergence analysis report")
            
            # Get convergence data
            convergence_data = {}
            if hasattr(optimizer, 'check_hypervolume_convergence'):
                convergence_data = optimizer.check_hypervolume_convergence()
            
            progress_summary = {}
            if hasattr(optimizer, 'get_optimization_progress_summary'):
                progress_summary = optimizer.get_optimization_progress_summary()
            
            # Prepare convergence report data
            report_data = {
                "report_title": "Convergence Analysis",
                "timestamp": datetime.now().isoformat(),
                "total_iterations": len(getattr(optimizer, 'iteration_history', [])),
                "total_experiments": len(getattr(optimizer, 'experimental_data', pd.DataFrame())),
                "convergence_status": convergence_data.get("recommendation", "unknown"),
                "converged": convergence_data.get("converged", False),
                "relative_improvement": convergence_data.get("relative_improvement", 0.0),
                "iterations_stable": convergence_data.get("iterations_stable", 0),
                "hypervolume_trend": progress_summary.get("hypervolume_trend", "unknown"),
                "efficiency_metrics": progress_summary.get("efficiency_metrics", {}),
                "recommendations": progress_summary.get("recommendations", []),
                "convergence_details": convergence_data,
                "progress_summary": progress_summary
            }
            
            # Add iteration history analysis
            iteration_history = getattr(optimizer, 'iteration_history', [])
            if iteration_history:
                hypervolume_history = []
                for iteration in iteration_history:
                    hv_value = iteration.get("hypervolume", 0.0)
                    if isinstance(hv_value, dict):
                        hypervolume_history.append(hv_value.get("raw_hypervolume", 0.0))
                    else:
                        hypervolume_history.append(hv_value)
                
                report_data["hypervolume_history"] = hypervolume_history
                
                if len(hypervolume_history) > 1:
                    report_data["convergence_metrics"] = {
                        "final_hypervolume": hypervolume_history[-1],
                        "max_hypervolume": max(hypervolume_history),
                        "improvement_rate": (hypervolume_history[-1] - hypervolume_history[0]) / max(hypervolume_history[0], 1e-8),
                        "stability_index": np.std(hypervolume_history[-5:]) / max(np.mean(hypervolume_history[-5:]), 1e-8) if len(hypervolume_history) >= 5 else 0.0
                    }
            
            # Generate report
            success = self._export_report_with_fallback(
                "convergence_analysis", report_data, output_format, filepath
            )
            
            return {
                "success": success,
                "report_type": "convergence_analysis",
                "converged": convergence_data.get("converged", False),
                "filepath": str(filepath) if filepath else None
            }
            
        except Exception as e:
            logger.error(f"Error generating convergence report: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def generate_parameter_sensitivity_report(
        self,
        optimizer: Any,
        output_format: str = "html",
        filepath: Union[str, Path] = None
    ) -> Dict[str, Any]:
        """
        Generate parameter sensitivity analysis report.
        
        Args:
            optimizer: The optimization engine instance
            output_format: Output format
            filepath: Path to save report
            
        Returns:
            Dictionary with report generation results
        """
        try:
            logger.info("Generating parameter sensitivity report")
            
            # Get response models for sensitivity analysis
            sensitivity_data = {}
            if hasattr(optimizer, 'get_response_models'):
                models = optimizer.get_response_models()
                param_names = list(getattr(optimizer, 'params_config', {}).keys())
                
                for response_name, model in models.items():
                    if hasattr(optimizer, 'get_feature_importances'):
                        importances = optimizer.get_feature_importances(response_name)
                        sensitivity_data[response_name] = importances
            
            # Prepare sensitivity report data
            report_data = {
                "report_title": "Parameter Sensitivity Analysis",
                "timestamp": datetime.now().isoformat(),
                "parameters": list(getattr(optimizer, 'params_config', {}).keys()),
                "responses": list(getattr(optimizer, 'responses_config', {}).keys()),
                "sensitivity_analysis": sensitivity_data,
                "total_experiments": len(getattr(optimizer, 'experimental_data', pd.DataFrame()))
            }
            
            # Calculate overall parameter importance
            if sensitivity_data:
                overall_importance = {}
                for param_name in report_data["parameters"]:
                    total_importance = 0.0
                    count = 0
                    for response_importances in sensitivity_data.values():
                        if param_name in response_importances:
                            total_importance += response_importances[param_name]
                            count += 1
                    
                    if count > 0:
                        overall_importance[param_name] = total_importance / count
                    else:
                        overall_importance[param_name] = 0.0
                
                report_data["overall_parameter_importance"] = overall_importance
                
                # Sort parameters by importance
                sorted_params = sorted(overall_importance.items(), key=lambda x: x[1], reverse=True)
                report_data["parameter_ranking"] = [{"parameter": param, "importance": importance} for param, importance in sorted_params]
            
            # Generate report
            success = self._export_report_with_fallback(
                "sensitivity_analysis", report_data, output_format, filepath
            )
            
            return {
                "success": success,
                "report_type": "sensitivity_analysis",
                "parameters_analyzed": len(report_data["parameters"]),
                "filepath": str(filepath) if filepath else None
            }
            
        except Exception as e:
            logger.error(f"Error generating sensitivity report: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _prepare_base_report_data(self, optimizer: Any) -> Dict[str, Any]:
        """Prepare base report data including project info, parameters, and best solutions."""
        try:
            # Get Pareto front
            pareto_X, pareto_obj, pareto_indices = optimizer.get_pareto_front() if hasattr(optimizer, 'get_pareto_front') else (pd.DataFrame(), pd.DataFrame(), np.array([]))
            
            # Get best solution
            best_params, best_responses = optimizer.get_best_compromise_solution() if hasattr(optimizer, 'get_best_compromise_solution') else ({}, {})
            
            return {
                "project_name": "Multi-Objective Optimization Study",
                "timestamp": datetime.now().isoformat(),
                "total_experiments": len(getattr(optimizer, 'experimental_data', pd.DataFrame())),
                "parameters": getattr(optimizer, 'params_config', {}),
                "objectives": getattr(optimizer, 'responses_config', {}),
                "constraints": getattr(optimizer, 'general_constraints', []),
                "final_hypervolume": optimizer._calculate_hypervolume_legacy() if hasattr(optimizer, '_calculate_hypervolume_legacy') else 0.0,
                "experimental_data": getattr(optimizer, 'experimental_data', pd.DataFrame()).to_dict("records"),
                "iteration_history": getattr(optimizer, 'iteration_history', []),
                "pareto_solutions": len(pareto_indices),
                "best_solution": {
                    "parameters": best_params,
                    "responses": best_responses,
                }
            }
        except Exception as e:
            logger.error(f"Error preparing base report data: {e}")
            return {
                "project_name": "Multi-Objective Optimization Study",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _gather_statistical_analysis_data(self, optimizer: Any) -> Dict[str, Any]:
        """Gather statistical analysis data including validation report."""
        try:
            if not self.scientific_validator:
                return {}
            
            experimental_data = getattr(optimizer, 'experimental_data', pd.DataFrame())
            params_config = getattr(optimizer, 'params_config', {})
            
            if experimental_data.empty or not params_config:
                return {}
            
            validation_report = self.scientific_validator.validate_experimental_data(
                experimental_data, params_config
            )
            
            return {
                "descriptive_statistics": validation_report["statistics"].get("descriptive", {}),
                "outlier_counts": validation_report["statistics"].get("outlier_counts", {}),
                "quality_score": validation_report["statistics"].get("quality_score", 0),
                "warnings": validation_report["warnings"],
                "errors": validation_report["errors"]
            }
        except Exception as e:
            logger.error(f"Error gathering statistical data: {e}")
            return {}
    
    def _calculate_correlations(self, optimizer: Any) -> Dict[str, float]:
        """Calculate correlations between numeric variables."""
        try:
            experimental_data = getattr(optimizer, 'experimental_data', pd.DataFrame())
            
            if experimental_data.empty:
                return {}
            
            numeric_data = experimental_data.select_dtypes(include=[np.number])
            correlations = {}
            
            if not numeric_data.empty and len(numeric_data.columns) > 1:
                corr_matrix = numeric_data.corr().stack().reset_index()
                corr_matrix.columns = ["var1", "var2", "correlation"]
                
                for _, row in corr_matrix.iterrows():
                    if (row["var1"] != row["var2"] and 
                        f"{row['var2']}-{row['var1']}" not in correlations):
                        correlations[f"{row['var1']}-{row['var2']}"] = row["correlation"]
            
            return correlations
        except Exception as e:
            logger.error(f"Error calculating correlations: {e}")
            return {}
    
    def _generate_plot_images(self, optimizer: Any, plot_configs: Dict[str, Any]) -> Dict[str, str]:
        """Generate plot images as base64 strings based on plot configurations."""
        plots_base64 = {}
        
        try:
            plot_manager = getattr(optimizer, 'plot_manager', None)
            if not plot_manager or not plot_configs:
                return plots_base64
            
            # Generate Pareto plot
            if plot_configs.get("pareto_plot", False):
                try:
                    fig_pareto = plt.figure(figsize=(8, 6))
                    pareto_X, pareto_obj, _ = optimizer.get_pareto_front()
                    
                    if hasattr(plot_manager, 'create_pareto_plot'):
                        objective_names = getattr(optimizer, 'objective_names', [])
                        plot_manager.create_pareto_plot(
                            fig_pareto,
                            None,
                            objective_names[0] if objective_names else "",
                            objective_names[1] if len(objective_names) > 1 else "",
                            pareto_X,
                            pareto_obj,
                        )
                        if self.report_generator and hasattr(self.report_generator, '_fig_to_base64'):
                            plots_base64["pareto_front_plot"] = self.report_generator._fig_to_base64(fig_pareto)
                    
                    plt.close(fig_pareto)
                except Exception as e:
                    logger.warning(f"Error generating Pareto plot: {e}")
            
            # Generate progress plot
            if plot_configs.get("progress_plot", False):
                try:
                    fig_progress = plt.figure(figsize=(8, 6))
                    if hasattr(plot_manager, 'create_progress_plot'):
                        plot_manager.create_progress_plot(fig_progress, None)
                        if self.report_generator and hasattr(self.report_generator, '_fig_to_base64'):
                            plots_base64["optimization_progress_plot"] = self.report_generator._fig_to_base64(fig_progress)
                    
                    plt.close(fig_progress)
                except Exception as e:
                    logger.warning(f"Error generating progress plot: {e}")
            
            return plots_base64
            
        except Exception as e:
            logger.error(f"Error generating plot images: {e}")
            return {}
    
    def _export_report_with_fallback(
        self, 
        report_type: str, 
        report_data: Dict[str, Any], 
        output_format: str, 
        filepath: Optional[Path], 
        plots_base64: Dict[str, str] = None
    ) -> bool:
        """Export report using enhanced generator with fallback to original generator."""
        try:
            if not filepath:
                return False
            
            filepath = Path(filepath)
            
            # Try using the enhanced report generator first
            if self.enhanced_generator:
                try:
                    self.enhanced_generator.generate_enhanced_report(
                        report_type=report_type,
                        data=report_data,
                        output_format=output_format,
                        filepath=filepath,
                    )
                    logger.info("Enhanced report generated successfully")
                    return True
                except Exception as enhanced_error:
                    logger.warning(f"Enhanced report generator failed: {enhanced_error}")
            
            # Fallback to original report generator
            if self.report_generator:
                try:
                    if output_format == "pdf":
                        self.report_generator.generate_report(
                            "optimization_report", report_data, "pdf", filepath, plots_base64 or {}
                        )
                    elif output_format == "html":
                        self.report_generator.generate_report(
                            "optimization_report", report_data, "html", filepath, plots_base64 or {}
                        )
                    elif output_format == "markdown":
                        markdown_content = self.report_generator.generate_report(
                            "optimization_report", report_data, "markdown"
                        )
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(markdown_content)
                    elif output_format == "json":
                        import json
                        with open(filepath, "w") as f:
                            json.dump(report_data, f, indent=2, default=str)
                    else:
                        raise ValueError(f"Unsupported report format: {output_format}")
                    
                    logger.info("Fallback report generated successfully")
                    return True
                except Exception as fallback_error:
                    logger.error(f"Fallback report generator failed: {fallback_error}")
            
            return False
            
        except Exception as e:
            logger.error(f"Error in report export: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear report generation cache."""
        with self._lock:
            self._report_cache.clear()
        logger.debug("Report controller cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get report cache statistics."""
        with self._lock:
            return {"cached_reports": len(self._report_cache)}