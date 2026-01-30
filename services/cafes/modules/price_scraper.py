# =================================================================================
# PROYECTO: PlanIA (Local Module)
# ARCHIVO: modules/price_scraper.py
# COPYRIGHT: © 2026 Fondo Thoth AC.
# LICENCIA: GPLv2 (Open Source para análisis de datos públicos).
# DESCRIPCIÓN: Actualiza costos unitarios de ingredientes desde fuentes externas.
# =================================================================================

import json
import random
from typing import Any


class PriceScraper:
    """
    Receives a BOM (Bill of Materials) JSON and updates ingredient costs.
    In production, this would connect to price APIs or web scraping sources.
    Currently implements a simulated lookup for demonstration purposes.
    """

    def __init__(self, lat: float = 0.0, lon: float = 0.0):
        """
        Initialize with geographic coordinates for regional pricing.

        Args:
            lat: Latitude of the business location.
            lon: Longitude of the business location.
        """
        self.lat = lat
        self.lon = lon
        # Simulated price database (item -> base cost MXN)
        self._price_db = {
            "harina": 25.0,
            "azucar": 30.0,
            "huevo": 4.5,
            "leche": 28.0,
            "mantequilla": 45.0,
            "chocolate": 80.0,
            "vainilla": 60.0,
            "levadura": 15.0,
            "sal": 8.0,
            "aceite": 35.0,
            "crema": 50.0,
            "queso": 90.0,
            "jamon": 120.0,
            "pollo": 85.0,
            "carne": 150.0,
            "verduras": 40.0,
            "frutas": 55.0,
        }

    def update_costs(self, bom_json: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Update the cost of each ingredient in the BOM.

        Args:
            bom_json: List of products, each with 'producto', 'precio_venta', and 'insumos' list.
                      Each insumo has 'item' and 'costo' (may be 0 or null).

        Returns:
            Updated BOM with non-zero costs for each ingredient.
        """
        updated_bom = []
        for product in bom_json:
            updated_product = product.copy()
            updated_insumos = []

            for insumo in product.get("insumos", []):
                item_name = insumo.get("item", "").lower().strip()
                current_cost = insumo.get("costo") or 0

                if current_cost == 0:
                    # Look up price from simulated database
                    base_price = self._lookup_price(item_name)
                    insumo_copy = insumo.copy()
                    insumo_copy["costo"] = base_price
                    insumo_copy["source"] = "scraper" if base_price > 0 else "not_found"
                    updated_insumos.append(insumo_copy)
                else:
                    updated_insumos.append(insumo)

            updated_product["insumos"] = updated_insumos
            updated_bom.append(updated_product)

        return updated_bom

    def _lookup_price(self, item_name: str) -> float:
        """
        Simulate looking up a price from external sources.

        Args:
            item_name: Name of the ingredient.

        Returns:
            Price in MXN. Returns 0 if not found.
        """
        # Check if we have a direct match
        for key, price in self._price_db.items():
            if key in item_name or item_name in key:
                # Add slight regional variation (+/- 10%)
                variation = random.uniform(0.9, 1.1)
                return round(price * variation, 2)
        return 0.0

    def calculate_product_cost(self, product: dict[str, Any]) -> float:
        """
        Calculate total cost of a single product based on its ingredients.

        Args:
            product: Dictionary with 'insumos' list.

        Returns:
            Sum of all ingredient costs.
        """
        total = 0.0
        for insumo in product.get("insumos", []):
            cantidad = insumo.get("cantidad", 1)
            costo = insumo.get("costo", 0)
            total += cantidad * costo
        return round(total, 2)


# ==================================================
# LOCAL TEST
# ==================================================
if __name__ == "__main__":
    scraper = PriceScraper(lat=29.0729, lon=-110.9559)

    sample_bom = [
        {
            "producto": "Pastel de Chocolate",
            "precio_venta": 500,
            "insumos": [
                {"item": "Harina", "cantidad": 2, "costo": 0},
                {"item": "Chocolate", "cantidad": 1, "costo": 0},
                {"item": "Huevo", "cantidad": 6, "costo": 0},
                {"item": "Azucar", "cantidad": 1, "costo": 0},
            ],
        },
        {
            "producto": "Pan de Queso",
            "precio_venta": 80,
            "insumos": [
                {"item": "Harina", "cantidad": 1, "costo": 0},
                {"item": "Queso", "cantidad": 0.5, "costo": 0},
            ],
        },
    ]

    updated = scraper.update_costs(sample_bom)
    print("Updated BOM:")
    print(json.dumps(updated, indent=2, ensure_ascii=False))

    for prod in updated:
        cost = scraper.calculate_product_cost(prod)
        print(f"  {prod['producto']}: Costo total = ${cost:.2f} MXN")
