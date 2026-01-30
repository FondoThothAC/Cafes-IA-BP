# =================================================================================
# PROYECTO: PlanIA (Local Module)
# ARCHIVO: modules/finance_calc.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: GPLv2 (Open Source para análisis de datos públicos).
# DESCRIPCIÓN: Calculadora financiera para TIR, VAN, Punto de Equilibrio y ROI.
# =================================================================================

import json
from typing import Any


class FinancialBrain:
    """
    Calculates financial metrics for business plans:
    - Break-even point (units and monetary)
    - Monthly cash flow projection (12 months)
    - ROI (Return on Investment)
    """

    def __init__(
        self,
        fixed_costs_monthly: float,
        initial_investment: float,
        bom_json: list[dict[str, Any]],
        usd_mxn: float = 1.0,
    ):
        """
        Initialize the financial calculator.

        Args:
            fixed_costs_monthly: Monthly fixed costs (rent, salaries, utilities).
            initial_investment: Total initial investment required.
            bom_json: Products with 'precio_venta' and 'insumos' (with costs).
            usd_mxn: USD to MXN exchange rate for imported goods adjustment.
        """
        self.fixed_costs = fixed_costs_monthly
        self.initial_investment = initial_investment
        self.bom = bom_json
        self.usd_mxn = usd_mxn

    def calculate_break_even(self) -> dict[str, Any]:
        """
        Calculate break-even point in units and monetary value.

        Assumes a weighted average contribution margin if multiple products exist.

        Returns:
            Dictionary with 'units', 'monetary', and 'margin_avg' keys.
        """
        total_margin = 0.0
        total_weight = 0
        product_details = []

        for product in self.bom:
            precio_venta = product.get("precio_venta", 0)
            costo_variable = self._calculate_variable_cost(product)
            margen = precio_venta - costo_variable

            if precio_venta > 0:
                margen_pct = (margen / precio_venta) * 100
            else:
                margen_pct = 0

            product_details.append({
                "producto": product.get("producto", "Unknown"),
                "precio_venta": precio_venta,
                "costo_variable": costo_variable,
                "margen_contribucion": round(margen, 2),
                "margen_pct": round(margen_pct, 2),
            })

            total_margin += margen
            total_weight += 1

        if total_weight == 0 or total_margin <= 0:
            return {
                "units": None,
                "monetary": None,
                "margin_avg": 0,
                "error": "No se puede calcular: margen de contribución <= 0",
                "products": product_details,
            }

        avg_margin = total_margin / total_weight
        break_even_units = self.fixed_costs / avg_margin
        break_even_monetary = break_even_units * (
            sum(p.get("precio_venta", 0) for p in self.bom) / len(self.bom)
        )

        return {
            "units": round(break_even_units, 2),
            "monetary": round(break_even_monetary, 2),
            "margin_avg": round(avg_margin, 2),
            "fixed_costs_monthly": self.fixed_costs,
            "products": product_details,
        }

    def project_cash_flow(self, monthly_units_sold: list[int]) -> dict[str, Any]:
        """
        Project monthly cash flow for 12 months.

        Args:
            monthly_units_sold: List of 12 integers representing units sold per month.

        Returns:
            Dictionary with monthly breakdown and annual totals.
        """
        if len(monthly_units_sold) != 12:
            return {"error": "Se requieren exactamente 12 valores de unidades vendidas."}

        # Calculate average price and variable cost per unit
        total_price = 0.0
        total_var_cost = 0.0
        count = len(self.bom) if self.bom else 1

        for product in self.bom:
            total_price += product.get("precio_venta", 0)
            total_var_cost += self._calculate_variable_cost(product)

        avg_price = total_price / count
        avg_var_cost = total_var_cost / count

        monthly_data = []
        cumulative = -self.initial_investment  # Start with initial investment as outflow

        for month, units in enumerate(monthly_units_sold, start=1):
            ingresos = units * avg_price
            costos_variables = units * avg_var_cost
            utilidad_bruta = ingresos - costos_variables
            utilidad_neta = utilidad_bruta - self.fixed_costs
            cumulative += utilidad_neta

            monthly_data.append({
                "mes": month,
                "unidades_vendidas": units,
                "ingresos": round(ingresos, 2),
                "costos_variables": round(costos_variables, 2),
                "costos_fijos": self.fixed_costs,
                "utilidad_neta": round(utilidad_neta, 2),
                "acumulado": round(cumulative, 2),
            })

        annual_revenue = sum(m["ingresos"] for m in monthly_data)
        annual_profit = sum(m["utilidad_neta"] for m in monthly_data)

        return {
            "inversion_inicial": self.initial_investment,
            "flujo_mensual": monthly_data,
            "resumen_anual": {
                "ingresos_totales": round(annual_revenue, 2),
                "utilidad_neta_total": round(annual_profit, 2),
                "saldo_final": round(cumulative, 2),
            },
        }

    def calculate_roi(self, annual_profit: float) -> dict[str, Any]:
        """
        Calculate Return on Investment.

        Args:
            annual_profit: Total annual net profit.

        Returns:
            Dictionary with ROI percentage and payback period.
        """
        if self.initial_investment == 0:
            return {"roi_pct": None, "payback_months": None, "error": "Inversión inicial = 0"}

        roi = (annual_profit / self.initial_investment) * 100

        if annual_profit > 0:
            payback_months = (self.initial_investment / annual_profit) * 12
        else:
            payback_months = None

        return {
            "inversion_inicial": self.initial_investment,
            "utilidad_anual": annual_profit,
            "roi_pct": round(roi, 2),
            "payback_months": round(payback_months, 1) if payback_months else None,
        }

    def _calculate_variable_cost(self, product: dict[str, Any]) -> float:
        """
        Calculate total variable cost of a product from its BOM.

        Args:
            product: Product dictionary with 'insumos' list.

        Returns:
            Total variable cost.
        """
        total = 0.0
        for insumo in product.get("insumos", []):
            cantidad = insumo.get("cantidad", 1)
            costo = insumo.get("costo", 0)
            # Apply USD adjustment if item is imported (simplified check)
            if insumo.get("importado", False):
                costo *= self.usd_mxn
            total += cantidad * costo
        return round(total, 2)


# ==================================================
# LOCAL TEST
# ==================================================
if __name__ == "__main__":
    sample_bom = [
        {
            "producto": "Pastel de Chocolate",
            "precio_venta": 500,
            "insumos": [
                {"item": "Harina", "cantidad": 2, "costo": 25},
                {"item": "Chocolate", "cantidad": 1, "costo": 80},
                {"item": "Huevo", "cantidad": 6, "costo": 4.5},
                {"item": "Azucar", "cantidad": 1, "costo": 30},
            ],
        },
    ]

    brain = FinancialBrain(
        fixed_costs_monthly=15000,
        initial_investment=100000,
        bom_json=sample_bom,
        usd_mxn=17.5,
    )

    # Break-even
    be = brain.calculate_break_even()
    print("Punto de Equilibrio:")
    print(json.dumps(be, indent=2, ensure_ascii=False))

    # Cash flow projection (simulated sales growth)
    monthly_sales = [30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]
    cf = brain.project_cash_flow(monthly_sales)
    print("\nFlujo de Efectivo Anual:")
    print(json.dumps(cf["resumen_anual"], indent=2))

    # ROI
    roi = brain.calculate_roi(cf["resumen_anual"]["utilidad_neta_total"])
    print("\nROI:")
    print(json.dumps(roi, indent=2))
