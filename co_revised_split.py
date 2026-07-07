
import pandas as pd
# Generic CO Split Function
def split_marks(total_marks, student_index):

    # Perfect Score
    if total_marks == 70:
        return 28, 28, 14

    # Candidate CO3 values
    if total_marks >= 65:
        co3_candidates = [14, 13]

    elif total_marks >= 55:
        co3_candidates = [13, 12, 11]

    elif total_marks >= 45:
        co3_candidates = [11, 10, 9]

    elif total_marks >= 35:
        co3_candidates = [9, 8, 7]

    else:
        co3_candidates = [7, 6, 5]

    # Offset Rotation
    offsets = [0, -1, 1, -2, 2]

    rotation = student_index % len(offsets)

    offsets = offsets[rotation:] + offsets[:rotation]

    # Try every combination
    for co3 in co3_candidates:

        remaining = total_marks - co3

        base = remaining // 2

        for offset in offsets:

            co1 = base + offset
            co2 = remaining - co1

            # ------------------------
            # Business Rules
            # ------------------------

            if co1 < 0:
                continue

            if co2 < 0:
                continue

            if co1 > 28:
                continue

            if co2 > 28:
                continue

            if abs(co1 - co2) > 3:
                continue

            if (co1 + co2 + co3) != total_marks:
                continue

            return co1, co2, co3

    raise ValueError(
        f"Unable to split marks = {total_marks}"
    )


# ---------------------------------------------------------
# Main Function
# ---------------------------------------------------------

def split_co_marks(calc_df):

    co1_list = []
    co2_list = []
    co3_m1_list = []

    co3_m2_list = []
    co4_list = []
    co5_list = []

    # ---------------- MT1 ----------------

    for i, mt1 in enumerate(calc_df["MT1"]):

        co1, co2, co3 = split_marks(mt1, i)

        co1_list.append(co1)
        co2_list.append(co2)
        co3_m1_list.append(co3)

    # ---------------- MT2 ----------------

    for i, mt2 in enumerate(calc_df["MT2"]):

        co4, co5, co3 = split_marks(mt2, i)

        co3_m2_list.append(co3)
        co4_list.append(co4)
        co5_list.append(co5)

    calc_df["CO1(28)"] = co1_list
    calc_df["CO2(28)"] = co2_list
    calc_df["CO3_M1(14)"] = co3_m1_list

    calc_df["CO3_M2(14)"] = co3_m2_list
    calc_df["CO4(28)"] = co4_list
    calc_df["CO5(28)"] = co5_list

    return calc_df