
import pandas as pd


def split_co_marks(calc_df):

    co1_list = []
    co2_list = []
    co3_m1_list = []

    co3_m2_list = []
    co4_list = []
    co5_list = []

    offsets = [0, -1, 1, -1, 1, 0]

    # ==========================
    # MT1
    # ==========================

    for i, mt1 in enumerate(calc_df["MT1"]):

        if mt1 == 70:

            co1 = 28
            co2 = 28
            co3 = 14

        else:

            # CO3 Variation

            if mt1 >= 65:
                co3 = 13 + (i % 2)

            elif mt1 >= 55:
                co3 = 11 + (i % 3)

            elif mt1 >= 45:
                co3 = 9 + (i % 3)

            elif mt1 >= 35:
                co3 = 7 + (i % 3)

            else:
                co3 = 5 + (i % 3)

            remaining = mt1 - co3

            base = remaining // 2

            co1 = base + offsets[i % len(offsets)]
            co2 = remaining - co1

            # Limits

            co1 = min(max(co1, 0), 28)
            co2 = min(max(co2, 0), 28)

            # Balance

            if abs(co1 - co2) > 3:

                avg = remaining // 2

                co1 = avg
                co2 = remaining - avg

        co1_list.append(co1)
        co2_list.append(co2)
        co3_m1_list.append(co3)

    # ==========================
    # MT2
    # ==========================

    for i, mt2 in enumerate(calc_df["MT2"]):

        if mt2 == 70:

            co3 = 14
            co4 = 28
            co5 = 28

        else:

            if mt2 >= 65:
                co3 = 13 + (i % 2)

            elif mt2 >= 55:
                co3 = 11 + (i % 3)

            elif mt2 >= 45:
                co3 = 9 + (i % 3)

            elif mt2 >= 35:
                co3 = 7 + (i % 3)

            else:
                co3 = 5 + (i % 3)

            remaining = mt2 - co3

            base = remaining // 2

            co4 = base + offsets[i % len(offsets)]
            co5 = remaining - co4

            co4 = min(max(co4, 0), 28)
            co5 = min(max(co5, 0), 28)

            if abs(co4 - co5) > 3:

                avg = remaining // 2

                co4 = avg
                co5 = remaining - avg

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