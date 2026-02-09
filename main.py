# -*- coding: utf-8 -*-
from app.util.s_splitter import rule_based_candidate_split

if __name__ == "__main__":
    sample = (
        "케르소네소스 지역의 참주는 키몬의 아들이자 스테사고라스의 손자 밀티아데스. "
        "돌롱코이 족이라는 트라키아 부족이 이웃 부족에게 밀리자 델포이 신탁을 구함. "
        "그러다가 킵셀로스의 아들 밀티아데스를 만남. "
        "마침 돌롱코이족이 처음 만나는 사람을 왕으로 삼으라는 신탁을 받음"
    )

    spans = rule_based_candidate_split(sample)
    for i, s in enumerate(spans, 1):
        print(f"{i:02d}. {s.text}")
