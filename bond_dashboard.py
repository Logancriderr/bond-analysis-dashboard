import math

import numpy as np
import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Corporate Bond Analytics Dashboard",
    page_icon="📈",
    layout="wide",
)


# ---------------------------------------------------------
# BOND CALCULATION FUNCTION
# ---------------------------------------------------------
def calculate_bond_metrics(
    coupon_rate: float,
    years_to_maturity: int,
    ytm: float,
    par_value: float,
    frequency: int,
) -> tuple[float, float, float, pd.DataFrame]:
    """
    Calculate a bond's value, Macaulay duration, modified duration,
    and period-by-period cash-flow table.

    Parameters
    ----------
    coupon_rate:
        Annual coupon rate expressed as a decimal.
        Example: 4% is entered as 0.04.

    years_to_maturity:
        Number of years until maturity.

    ytm:
        Annual yield to maturity expressed as a decimal.
        Example: 8% is entered as 0.08.

    par_value:
        Bond face value.

    frequency:
        Number of coupon payments per year.

    Returns
    -------
    bond_value:
        Present value of all bond cash flows.

    macaulay_duration:
        Macaulay duration expressed in years.

    modified_duration:
        Modified duration expressed in years.

    cash_flow_table:
        DataFrame containing the duration calculations.
    """

    # Convert annual inputs to periodic inputs.
    periodic_coupon = par_value * coupon_rate / frequency
    periodic_yield = ytm / frequency

    # A conventional coupon bond needs a whole number of payment periods.
    raw_number_of_periods = years_to_maturity * frequency
    number_of_periods = years_to_maturity * frequency

    if not math.isclose(
        raw_number_of_periods,
        number_of_periods,
        rel_tol=0,
        abs_tol=1e-9,
    ):
        raise ValueError(
            "The maturity and payment frequency must produce a whole "
            "number of coupon periods."
        )

    periods = np.arange(1, number_of_periods + 1)

    # All periods receive a coupon payment.
    cash_flows = np.full(
        number_of_periods,
        periodic_coupon,
        dtype=float,
    )

    # The final period also returns the bond's par value.
    cash_flows[-1] += par_value

    # Discount each cash flow.
    discount_factors = (1 + periodic_yield) ** periods
    present_values = cash_flows / discount_factors

    bond_value = float(present_values.sum())

    # Macaulay duration is first calculated in payment periods.
    weighted_present_values = periods * present_values
    macaulay_duration_periods = (
        weighted_present_values.sum() / bond_value
    )

    # Convert duration from payment periods to years.
    macaulay_duration = (
        macaulay_duration_periods / frequency
    )

    # Modified duration adjusts Macaulay duration for the periodic yield.
    modified_duration = (
        macaulay_duration / (1 + periodic_yield)
    )

    cash_flow_table = pd.DataFrame(
        {
            "Period": periods,
            "Time (Years)": periods / frequency,
            "Cash Flow": cash_flows,
            "Discount Factor": discount_factors,
            "Present Value": present_values,
            "Period × Present Value": weighted_present_values,
        }
    )

    return (
        bond_value,
        macaulay_duration,
        modified_duration,
        cash_flow_table,
    )


# ---------------------------------------------------------
# GRAPH DATA FUNCTION
# ---------------------------------------------------------
def create_yield_curve_data(
    coupon_rate: float,
    years_to_maturity: float,
    par_value: float,
    frequency: int,
    selected_ytm: float,
) -> pd.DataFrame:
    """
    Create bond prices over a reasonable range of YTMs.
    """

    # Keep all graph yields nonnegative.
    minimum_yield = max(0.0, selected_ytm - 0.06)
    maximum_yield = selected_ytm + 0.06

    yield_values = np.linspace(
        minimum_yield,
        maximum_yield,
        50,
    )

    bond_values = []

    for graph_ytm in yield_values:
        value, _, _, _ = calculate_bond_metrics(
            coupon_rate=coupon_rate,
            years_to_maturity=years_to_maturity,
            ytm=graph_ytm,
            par_value=par_value,
            frequency=frequency,
        )
        bond_values.append(value)

    return pd.DataFrame(
        {
            "Yield to Maturity (%)": yield_values * 100,
            "Bond Value ($)": bond_values,
        }
    )


# ---------------------------------------------------------
# DASHBOARD TITLE
# ---------------------------------------------------------
st.title("Corporate Bond Analytics Dashboard")

st.write(
    "Enter the bond assumptions below to calculate its value, "
    "Macaulay duration, and modified duration."
)


# ---------------------------------------------------------
# SIDEBAR INPUTS
# ---------------------------------------------------------
st.sidebar.header("Bond Inputs")

coupon_rate_percent = st.sidebar.number_input(
    "Annual Coupon Rate (%)",
    min_value=0.0,
    max_value=100.0,
    value=4.0,
    step=0.25,
    help="Enter the stated annual coupon rate as a percentage.",
)

years_to_maturity = st.sidebar.number_input(
    "Term to Maturity (Years)",
    min_value=1,
    max_value=100,
    value=6,
    step=1,
    help="Enter the number of whole years until the bond matures.",
)

ytm_percent = st.sidebar.number_input(
    "Annual Yield to Maturity (%)",
    min_value=0.0,
    max_value=100.0,
    value=8.0,
    step=0.25,
    help="Enter the stated annual YTM as a percentage.",
)

par_value = st.sidebar.number_input(
    "Par Value ($)",
    min_value=0.01,
    max_value=100_000_000.0,
    value=1_000.0,
    step=100.0,
    format="%.2f",
    help="Par value must be greater than zero.",
)

frequency_label = st.sidebar.selectbox(
    "Compounding and Payment Frequency",
    options=[
        "Annual",
        "Semiannual",
        "Quarterly",
        "Monthly",
    ],
    index=1,
)

frequency_map = {
    "Annual": 1,
    "Semiannual": 2,
    "Quarterly": 4,
    "Monthly": 12,
}

frequency = frequency_map[frequency_label]


# Convert percentages to decimals for calculations.
coupon_rate = coupon_rate_percent / 100
ytm = ytm_percent / 100


# ---------------------------------------------------------
# INPUT VALIDATION
# ---------------------------------------------------------
inputs_are_valid = True

if par_value <= 0:
    st.error("Par value must be greater than zero.")
    inputs_are_valid = False

if coupon_rate < 0:
    st.error("The coupon rate cannot be negative.")
    inputs_are_valid = False

if ytm < 0:
    st.error("The yield to maturity cannot be negative.")
    inputs_are_valid = False

if years_to_maturity <= 0:
    st.error("The term to maturity must be greater than zero.")
    inputs_are_valid = False

# ---------------------------------------------------------
# CALCULATIONS AND OUTPUT
# ---------------------------------------------------------
if inputs_are_valid:
    try:
        (
            bond_value,
            macaulay_duration,
            modified_duration,
            duration_table,
        ) = calculate_bond_metrics(
            coupon_rate=coupon_rate,
            years_to_maturity=years_to_maturity,
            ytm=ytm,
            par_value=par_value,
            frequency=frequency,
        )

    except (ValueError, ZeroDivisionError, OverflowError) as error:
        st.error(f"The bond could not be calculated: {error}")

    else:
        st.subheader("Bond Valuation Results")

        result_column_1, result_column_2, result_column_3 = st.columns(3)

        with result_column_1:
            st.metric(
                label="Bond Value",
                value=f"${bond_value:,.2f}",
            )

        with result_column_2:
            st.metric(
                label="Macaulay Duration",
                value=f"{macaulay_duration:,.4f} years",
            )

        with result_column_3:
            st.metric(
                label="Modified Duration",
                value=f"{modified_duration:,.4f} years",
            )

        # -------------------------------------------------
        # INTERMEDIATE CALCULATIONS
        # -------------------------------------------------
        st.subheader("Calculation Summary")

        periodic_coupon = (
            par_value * coupon_rate / frequency
        )
        periodic_yield = ytm / frequency
        number_of_periods = round(
            years_to_maturity * frequency
        )

        summary_data = pd.DataFrame(
            {
                "Calculation": [
                    "Annual Coupon Rate",
                    "Annual Yield to Maturity",
                    "Payments per Year",
                    "Number of Payment Periods",
                    "Coupon Payment per Period",
                    "Yield per Period",
                ],
                "Result": [
                    f"{coupon_rate:.2%}",
                    f"{ytm:.2%}",
                    f"{frequency}",
                    f"{number_of_periods}",
                    f"${periodic_coupon:,.2f}",
                    f"{periodic_yield:.4%}",
                ],
            }
        )

        st.dataframe(
            summary_data,
            hide_index=True,
            width="stretch",
        )

        # -------------------------------------------------
        # DURATION TABLE
        # -------------------------------------------------
        st.subheader("Macaulay Duration Table")

        formatted_duration_table = duration_table.copy()

        formatted_duration_table["Time (Years)"] = (
            formatted_duration_table["Time (Years)"].map(
                lambda value: f"{value:,.4f}"
            )
        )

        formatted_duration_table["Cash Flow"] = (
            formatted_duration_table["Cash Flow"].map(
                lambda value: f"${value:,.2f}"
            )
        )

        formatted_duration_table["Discount Factor"] = (
            formatted_duration_table["Discount Factor"].map(
                lambda value: f"{value:,.6f}"
            )
        )

        formatted_duration_table["Present Value"] = (
            formatted_duration_table["Present Value"].map(
                lambda value: f"${value:,.2f}"
            )
        )

        formatted_duration_table["Period × Present Value"] = (
            formatted_duration_table[
                "Period × Present Value"
            ].map(lambda value: f"${value:,.2f}")
        )

        st.dataframe(
            formatted_duration_table,
            hide_index=True,
            width="stretch",
        )

        st.caption(
            "Macaulay duration equals the sum of period-weighted "
            "present values divided by the bond value, converted "
            "from payment periods to years."
        )

        # -------------------------------------------------
        # PRICE-YIELD GRAPH
        # -------------------------------------------------
        st.subheader("Bond Value/Yield Graph")

        graph_data = create_yield_curve_data(
            coupon_rate=coupon_rate,
            years_to_maturity=years_to_maturity,
            par_value=par_value,
            frequency=frequency,
            selected_ytm=ytm,
        )

        st.line_chart(
            graph_data,
            x="Yield to Maturity (%)",
            y="Bond Value ($)",
            x_label="Yield to Maturity (%)",
            y_label="Bond Value ($)",
            width="stretch",
        )

        st.caption(
            "The downward-sloping graph demonstrates the inverse "
            "relationship between bond values and yields."
        )

        # -------------------------------------------------
        # INTERPRETATION
        # -------------------------------------------------
        st.subheader("Interpretation")

        if bond_value < par_value:
            pricing_status = "a discount"
            explanation = (
                "the coupon rate is below the yield to maturity"
            )
        elif bond_value > par_value:
            pricing_status = "a premium"
            explanation = (
                "the coupon rate is above the yield to maturity"
            )
        else:
            pricing_status = "par value"
            explanation = (
                "the coupon rate equals the yield to maturity"
            )

        st.write(
            f"The bond is valued at **${bond_value:,.2f}**, so it "
            f"trades at **{pricing_status}** because {explanation}. "
            f"Its Macaulay duration is **{macaulay_duration:.4f} "
            f"years**, while its modified duration is "
            f"**{modified_duration:.4f} years**."
        )