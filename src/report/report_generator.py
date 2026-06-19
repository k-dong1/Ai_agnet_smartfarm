import os
import pandas as pd
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from config.settings import BASE_DIR, OUTPUT_DIR
from src.report.chart_generator import (
    generate_loss_chart, 
    generate_sensor_trend_chart,
    generate_importance_chart
)

def generate_report(agent_result: dict, metrics: dict, df: pd.DataFrame, output_filename: str = "report.html",
                    station_name: str = "전국 (전체)", gray_mold_detail: dict = None, whitefly_detail: dict = None) -> str:
    """
    Generates Matplotlib charts and renders the analysis results into a premium HTML report.
    
    Args:
        agent_result: Dict returned by SmartFarmAgent.run_agent_analysis.
        metrics: Dict containing MLP training metrics.
        df: pd.DataFrame containing historical/recent sensor readings.
        output_filename: The name of the HTML file to be generated.
        station_name: Target station or farm name.
        gray_mold_detail: Detailed info of gray mold from NCPMS.
        whitefly_detail: Detailed info of whitefly from NCPMS.
        
    Returns:
        str: Absolute path of the generated HTML report.
    """
    # 1. Generate Matplotlib Charts
    charts_dir = os.path.join(OUTPUT_DIR, "charts")
    loss_history = metrics.get("loss_history", [])
    feature_importance = metrics.get("feature_importance", {})
    
    loss_chart_rel_path = ""
    trend_chart_rel_path = ""
    importance_chart_rel_path = ""
    
    try:
        if loss_history:
            generate_loss_chart(loss_history, charts_dir)
            loss_chart_rel_path = "charts/loss_curve.png"
    except Exception as e:
        print(f"Warning: Failed to generate training loss chart: {e}")
        
    try:
        if not df.empty:
            generate_sensor_trend_chart(df, charts_dir)
            trend_chart_rel_path = "charts/sensor_trend.png"
    except Exception as e:
        print(f"Warning: Failed to generate sensor trend chart: {e}")

    try:
        if feature_importance:
            generate_importance_chart(feature_importance, charts_dir)
            importance_chart_rel_path = "charts/feature_importance.png"
    except Exception as e:
        print(f"Warning: Failed to generate feature importance chart: {e}")
        
    # 2. Render HTML Template
    templates_dir = os.path.join(BASE_DIR, "src", "report", "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("report_template.html")
    
    render_params = {
        "risk_level": agent_result["risk_level"],
        "risk_label": agent_result["risk_label"],
        "sensor_data": agent_result["sensor_data"],
        "risk_probability": agent_result["risk_probability"],
        "reasons": agent_result["reasons"],
        "actions": agent_result["actions"],
        "llm_summary": agent_result["llm_summary"],
        "logs": agent_result["logs"],
        "metrics": metrics,
        "loss_chart_path": loss_chart_rel_path,
        "trend_chart_path": trend_chart_rel_path,
        "importance_chart_path": importance_chart_rel_path,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "station_name": station_name,
        "gray_mold_detail": gray_mold_detail or {},
        "whitefly_detail": whitefly_detail or {}
    }
    
    html_content = template.render(**render_params)
    
    # 3. Write report to file
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"[ReportGenerator] HTML Report generated successfully at: {output_path}")
    return output_path
