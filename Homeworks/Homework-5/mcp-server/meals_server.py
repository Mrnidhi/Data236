import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("meals")

API_BASE = "https://www.themealdb.com/api/json/v1/1"


@mcp.tool()
def search_meals_by_name(query: str, limit: int = 5) -> list[dict]:
    """Search TheMealDB for meals matching a name query."""
    resp = httpx.get(f"{API_BASE}/search.php", params={"s": query}, timeout=10)
    data = resp.json().get("meals") or []
    results = []
    for m in data[:limit]:
        results.append({
            "name": m["strMeal"],
            "area": m["strArea"],
            "category": m["strCategory"],
            "thumbnail": m["strMealThumb"],
            "id": m["idMeal"],
        })
    return results


@mcp.tool()
def meals_by_ingredient(ingredient: str, limit: int = 12) -> list[dict]:
    """Filter meals by a main ingredient."""
    resp = httpx.get(f"{API_BASE}/filter.php", params={"i": ingredient}, timeout=10)
    data = resp.json().get("meals") or []
    results = []
    for m in data[:limit]:
        results.append({
            "name": m["strMeal"],
            "thumbnail": m["strMealThumb"],
            "id": m["idMeal"],
        })
    return results


@mcp.tool()
def meal_details(meal_id: str) -> dict:
    """Look up full details for a meal by its ID (instructions, ingredients, etc)."""
    resp = httpx.get(f"{API_BASE}/lookup.php", params={"i": meal_id}, timeout=10)
    data = resp.json().get("meals")
    if not data:
        return {"error": "Meal not found"}
    m = data[0]

    # collect non-empty ingredient + measure pairs
    ingredients = []
    for i in range(1, 21):
        ing = (m.get(f"strIngredient{i}") or "").strip()
        meas = (m.get(f"strMeasure{i}") or "").strip()
        if ing:
            ingredients.append(f"{meas} {ing}".strip())

    return {
        "name": m["strMeal"],
        "category": m["strCategory"],
        "area": m["strArea"],
        "instructions": m["strInstructions"],
        "thumbnail": m["strMealThumb"],
        "ingredients": ingredients,
        "youtube": m.get("strYoutube", ""),
        "source": m.get("strSource", ""),
    }


@mcp.tool()
def random_meal() -> dict:
    """Fetch a single random meal from TheMealDB."""
    resp = httpx.get(f"{API_BASE}/random.php", timeout=10)
    data = resp.json().get("meals")
    if not data:
        return {"error": "No meal returned"}
    m = data[0]
    return {
        "name": m["strMeal"],
        "area": m["strArea"],
        "category": m["strCategory"],
        "thumbnail": m["strMealThumb"],
        "id": m["idMeal"],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
