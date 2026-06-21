from config.thresholds import (
    HUMIDITY_CAUTION,
    HUMIDITY_SEVERE,
    LOW_TEMP_THRESHOLD,
    HIGH_TEMP_THRESHOLD,
    HUMIDITY_CHANGE_THRESHOLD,
    TEMP_CHANGE_THRESHOLD
)

def analyze_risk_reasons(sensor_data: dict) -> list:
    """
    Analyzes the sensor features to identify specific risk factors contributing to gray mold or whitefly.
    
    Args:
        sensor_data: A dictionary of sensor readings.
        
    Returns:
        list: A list of risk reasons (strings).
    """
    reasons = []
    
    humidity = sensor_data.get("humidity", 0.0)
    temperature = sensor_data.get("temperature", 20.0)
    humidity_duration = sensor_data.get("humidity_duration", 0)
    humidity_change = sensor_data.get("humidity_change", 0.0)
    temp_change = sensor_data.get("temp_change", 0.0)

    # 1. Humidity Analysis
    if humidity >= HUMIDITY_SEVERE:
        reasons.append(f"현재 습도가 {humidity:.1f}%로 심각한 고습 환경입니다. 잿빛곰팡이병균 포자 형성과 발아가 매우 활발해질 위험이 있습니다.")
    elif humidity >= HUMIDITY_CAUTION:
        reasons.append(f"현재 습도가 {humidity:.1f}%로 다습한 상태입니다. 잿빛곰팡이병 전염에 유리한 조건이 될 수 있습니다.")

    # 2. Temperature Analysis
    if temperature <= LOW_TEMP_THRESHOLD:
        reasons.append(f"온도가 {temperature:.1f}℃로 저온 환경입니다. 저온다습 상태가 유지되면 잿빛곰팡이병 발생 확률이 급증합니다.")
    elif temperature >= HIGH_TEMP_THRESHOLD:
        reasons.append(f"온도가 {temperature:.1f}℃로 고온 환경입니다. 환기가 제대로 되지 않을 시 담배가루이의 증식 속도가 빨라질 수 있습니다.")

    # 3. Adverse condition duration
    if humidity_duration >= 3:
        reasons.append(f"습도 {HUMIDITY_CAUTION}% 이상의 다습 상태가 {humidity_duration}회 연속 관측되어 고습 상태가 누적되고 있습니다.")

    # 4. Stress factors (sudden changes)
    if abs(humidity_change) >= HUMIDITY_CHANGE_THRESHOLD:
        sign = "상승" if humidity_change > 0 else "하락"
        reasons.append(f"습도가 이전 대비 급격히 {sign}(변화량: {humidity_change:+.1f}%)하여 환경 스트레스가 발생할 수 있습니다.")
    if abs(temp_change) >= TEMP_CHANGE_THRESHOLD:
        sign = "상승" if temp_change > 0 else "하락"
        reasons.append(f"온도가 이전 대비 급격히 {sign}(변화량: {temp_change:+.1f}℃)하여 일교차 또는 온실 스트레스가 감지되었습니다.")

    if not reasons:
        reasons.append("환경 데이터 분석 결과 온실 내 온습도 및 환기 상태가 안정적이며 위험 요인이 없습니다.")

    return reasons
