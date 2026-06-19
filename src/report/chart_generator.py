import os
import matplotlib
# Force Matplotlib to use a non-interactive backend (agg) to prevent GUI errors
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def generate_loss_chart(loss_history: list, output_dir: str) -> str:
    """
    Plots the MLP model training loss curve styled for a dark dashboard.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure Matplotlib dark style parameters
    plt.rcParams['text.color'] = '#f8fafc'
    plt.rcParams['axes.labelcolor'] = '#94a3b8'
    plt.rcParams['xtick.color'] = '#94a3b8'
    plt.rcParams['ytick.color'] = '#94a3b8'
    
    fig, ax = plt.subplots(figsize=(6, 3.5), facecolor='none')
    ax.set_facecolor('none')
    
    # Plot line
    epochs = range(1, len(loss_history) + 1)
    ax.plot(epochs, loss_history, color='#38bdf8', linewidth=2.5, label='Loss')
    
    # Fill under curve
    ax.fill_between(epochs, loss_history, color='#38bdf8', alpha=0.15)
    
    ax.set_title("Training Loss Curve", fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel("Epoch", fontsize=9)
    ax.set_ylabel("Loss", fontsize=9)
    
    # Style spines and grid
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#334155')
    ax.spines['bottom'].set_color('#334155')
    ax.grid(True, color='#334155', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    chart_path = os.path.join(output_dir, "loss_curve.png")
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', transparent=True)
    plt.close()
    
    return chart_path

def generate_sensor_trend_chart(df: pd.DataFrame, output_dir: str) -> str:
    """
    Plots dual-axis Temperature and Humidity trends for the latest 20 sensor records.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Keep only the latest 20 rows
    df_recent = df.tail(20).copy()
    
    # Convert index (collectDate) to simple string format
    if isinstance(df_recent.index, pd.DatetimeIndex):
        df_recent['time_str'] = df_recent.index.strftime('%m/%d %H:%M')
    else:
        df_recent['time_str'] = [str(t)[-8:-3] if len(str(t)) >= 8 else str(t) for t in df_recent.index]
        
    plt.rcParams['text.color'] = '#f8fafc'
    plt.rcParams['axes.labelcolor'] = '#94a3b8'
    
    fig, ax1 = plt.subplots(figsize=(10, 3.5), facecolor='none')
    ax1.set_facecolor('none')
    
    # X ticks spacing
    x_ticks = np.arange(len(df_recent))
    
    # Primary axis - Temperature (Orange)
    color_temp = '#f97316'
    ax1.set_xlabel('Time', color='#94a3b8', fontsize=9)
    ax1.set_ylabel('Temp (C)', color=color_temp, fontsize=9)
    ax1.plot(x_ticks, df_recent['temperature'], color=color_temp, marker='o', linewidth=2, label='Temp')
    ax1.tick_params(axis='y', labelcolor=color_temp)
    ax1.tick_params(axis='x', colors='#94a3b8')
    plt.xticks(x_ticks, df_recent['time_str'], rotation=45, fontsize=8)
    
    # Secondary axis - Humidity (Green)
    ax2 = ax1.twinx()
    color_hum = '#10b981'
    ax2.set_ylabel('Humidity (%)', color=color_hum, fontsize=9)
    ax2.plot(x_ticks, df_recent['humidity'], color=color_hum, marker='x', linewidth=2, linestyle='--', label='Hum')
    ax2.tick_params(axis='y', labelcolor=color_hum)
    
    # Style spines and grid
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.spines['left'].set_color('#334155')
    ax1.spines['bottom'].set_color('#334155')
    ax2.spines['right'].set_color('#334155')
    
    ax1.grid(True, color='#334155', linestyle='--', alpha=0.3)
    
    plt.title("Sensor Readings Trend (Latest 20 Records)", fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    chart_path = os.path.join(output_dir, "sensor_trend.png")
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', transparent=True)
    plt.close()
    
    return chart_path

def generate_importance_chart(importance_dict: dict, output_dir: str) -> str:
    """
    Plots a premium horizontal bar chart showing MLP feature importances.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Sort items by importance value
    sorted_items = sorted(importance_dict.items(), key=lambda x: x[1], reverse=False)
    features = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    plt.rcParams['text.color'] = '#f8fafc'
    plt.rcParams['axes.labelcolor'] = '#94a3b8'
    plt.rcParams['xtick.color'] = '#94a3b8'
    plt.rcParams['ytick.color'] = '#94a3b8'
    
    fig, ax = plt.subplots(figsize=(6, 3.5), facecolor='none')
    ax.set_facecolor('none')
    
    # Plot horizontal bars
    bars = ax.barh(features, values, color='#ec4899', height=0.6, edgecolor='none', alpha=0.9)
    
    # Add values text next to the bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.1f}%", 
                va='center', ha='left', fontsize=8, color='#f8fafc', fontweight='semibold')
                
    ax.set_title("MLP Model Feature Importance (XAI)", fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Relative Influence (%)", fontsize=9)
    
    # Style axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#334155')
    ax.spines['bottom'].set_color('#334155')
    ax.grid(True, axis='x', color='#334155', linestyle='--', alpha=0.4)
    
    # Set limit to allow text visibility
    if values:
        ax.set_xlim(0, max(values) * 1.15)
        
    plt.tight_layout()
    chart_path = os.path.join(output_dir, "feature_importance.png")
    plt.savefig(chart_path, dpi=150, bbox_inches='tight', transparent=True)
    plt.close()
    
    return chart_path
