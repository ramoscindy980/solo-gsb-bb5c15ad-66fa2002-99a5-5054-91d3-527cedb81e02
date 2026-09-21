"""分歧仲裁会话：把两轮已完成评审的共识判断预填进新会话，分歧组合留待评审。

创建前提（由 API 层校验，与「会话对照报告」一致）：

- 两会话的**启用候选名称集合完全相同**（候选录入顺序可以不同）；
- 两轮评审均已完成（启用候选之间的每个组合都已有判断）。

归一化口径与对照报告相同：每条判断按**候选名称字符串排序**为无向组合
并换算为**绝对胜者**（平局无胜者），与两轮候选录入顺序、存储时的 a/b
方向均无关，因此两轮组合结果逐对对齐后才比较异同。

仲裁会话规则：

- 新会话候选沿用**当前会话的启用候选顺序**（停用候选不进入仲裁会话）；
- 仅预填两轮结果**相同**（共识）的判断——同一绝对胜者，或两轮同为平局；
- 分歧组合（胜者反转 / 胜负变平局 / 平局变胜负）一律不预填，保持待评审。
"""
from __future__ import annotations

from itertools import combinations

from .compare import normalized_verdicts


def build_arbitration_judgments(
    candidates: list[str],
    history_a: list[dict],
    history_b: list[dict],
) -> tuple[list[dict], int, int]:
    """计算仲裁会话的预填判断（仅共识组合）。

    ``candidates`` 为新会话候选顺序（当前会话的启用候选顺序）；两轮历史
    先各自归一化为「名称序无向组合 → 绝对胜者」再逐对比较，结果与两轮
    候选录入顺序、存储 a/b 方向均无关。调用方已保证两轮均已完成且启用
    候选名称集合相同，因此每个名称序组合在两轮中都有归一化结果。

    返回 ``(预填判断列表, 共识数, 分歧数)``：预填判断按新会话候选录入
    顺序的组合顺序排列，组合按录入顺序存储（a 为录入序在前者），
    ``result`` 相对存储顺序的 a 解释——与正式评审接口的存储约定完全一致。
    """
    verdicts_a = normalized_verdicts(history_a)
    verdicts_b = normalized_verdicts(history_b)

    judgments: list[dict] = []
    agreed = disputed = 0
    for a, b in combinations(candidates, 2):
        lo, hi = (a, b) if a <= b else (b, a)
        winner_a = verdicts_a[(lo, hi)]
        winner_b = verdicts_b[(lo, hi)]
        if winner_a != winner_b:
            # 分歧组合（含胜者反转 / 胜负变平局 / 平局变胜负）：保持待评审
            disputed += 1
            continue
        agreed += 1
        if winner_a is None:
            result = "tie"
        else:
            # 绝对胜者换算回相对存储顺序（录入序在前者为 a）的结果
            result = "a" if winner_a == a else "b"
        judgments.append({"a": a, "b": b, "result": result})
    return judgments, agreed, disputed
