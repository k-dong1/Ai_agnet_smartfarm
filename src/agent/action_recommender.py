def recommend_actions(risk_label: int, reasons: list) -> list:
    """
    Recommends specific mitigation actions based on the predicted risk label
    and identified environmental reasons.
    
    Args:
        risk_label: int (0=Normal, 1=Caution, 2=Warning, 3=Severe)
        reasons: list of strings (reasons identified by the analyzer)
        
    Returns:
        list: Recommended actions (strings)
    """
    actions = []
    
    # 1. Base Recommendations on Risk Level
    if risk_label == 0:  # 정상
        actions.append("현재 관측된 위험 요인이 없습니다. 표준 온실 환경 프로파일에 따라 환기 및 일조 관리를 유지해 주십시오.")
        actions.append("주기적인 예찰을 통해 작물 상태를 정기 점검하십시오.")
        
    elif risk_label == 1:  # 주의
        actions.append("온실 내 다습을 방지하기 위해 유동팬을 가동하거나 천창/측창을 열어 환기율을 높이십시오.")
        actions.append("잿빛곰팡이병 의심 잎이나 열매가 발견되면 즉시 제거하고 소각 처리하십시오.")
        
    elif risk_label == 2:  # 경고
        actions.append("온실 환경을 건조하게 관리해야 합니다. 난방기를 가동하여 실내 온도를 높이고 강제 환기를 시도하십시오.")
        actions.append("토양 표면이 과도하게 젖지 않도록 관수량을 일시적으로 조절하십시오.")
        actions.append("잿빛곰팡이병 전용 등록 약제(살균제) 또는 담배가루이 전용 살충제(생물학적 제제 또는 화학적 농약) 살포 준비를 고려하십시오.")
        
    elif risk_label == 3:  # 심각
        actions.append("잿빛곰팡이병균 및 담배가루이가 급격히 확산될 수 있습니다. 온실 차단 조치와 더불어 긴급 방제(등록 약제 살포)를 실시하십시오.")
        actions.append("병든 식물체는 즉시 제거하여 전염원을 완벽히 격리하십시오.")
        actions.append("야간 온도 강하를 막기 위해 난방 온도를 높이고 습도를 적극적으로 70% 이하로 제어하십시오.")

    # 2. Add Context-specific Recommendations based on Reasons
    has_high_humidity = any("습도" in r and ("고습" in r or "다습" in r) for r in reasons)
    has_low_temp = any("온도" in r and "저온" in r for r in reasons)
    has_high_temp = any("온도" in r and "고온" in r for r in reasons)

    if has_high_humidity and risk_label >= 1:
        actions.append("적극적인 환기장치(순환팬, 유동팬) 가동 및 배습 처리를 실시간으로 가동하십시오.")
    if has_low_temp and risk_label >= 1:
        actions.append("야간 난방 온도를 최소 15℃ 이상으로 확보하여 저온 환경을 타개하십시오.")
    if has_high_temp and risk_label >= 1:
        actions.append("시설 외부 차광막을 가동하여 급격한 일사량 및 온도 증가를 막고, 황색 끈끈이 트랩을 늘려 담배가루이 밀도를 감시하십시오.")

    # Remove duplicates preserving order
    actions = list(dict.fromkeys(actions))
    
    return actions
