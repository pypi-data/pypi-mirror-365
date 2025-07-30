# 🥑 Avocavo Nutrition API Python SDK

[![PyPI version](https://badge.fury.io/py/avocavo-nutrition.svg)](https://badge.fury.io/py/avocavo-nutrition)
[![Python Support](https://img.shields.io/pypi/pyversions/avocavo-nutrition.svg)](https://pypi.org/project/avocavo-nutrition/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/avocavo-nutrition)](https://pepy.tech/projects/avocavo-nutrition)

**Bulletproof nutrition data with anti-hallucination protection + enterprise-grade secure credential storage.**

Get 100% reliable USDA nutrition data powered by our bulletproof system. Multi-tier caching, intelligent parsing, and mathematical calculations ensure accuracy. Real FDC IDs, sub-second responses, and accepts any ingredient description format. **Built-in secure keyring storage** keeps your API credentials safe. Perfect for recipe apps, fitness trackers, meal planners, and food tech products.

### ✨ Key Features
- ✅ **Secure credential storage** - System keyring integration (macOS/Windows/Linux)
- ✅ **100% USDA verified** - Real FDC IDs with every response
- ✅ **Anti-hallucination** - GPT never provides nutrition data
- ✅ **Sub-second responses** - Multi-tier caching system
- ✅ **Any input format** - Natural language processing
- ✅ **Production ready** - OAuth, server-side key management, batch processing

## 🚀 Quick Start

### Installation

```bash
pip install avocavo-nutrition
```

### 🔐 Two-Step Authentication (Recommended)

Modern OAuth + API key system for maximum security:

```python
import avocavo_nutrition as av

# Step 1: OAuth login (stores JWT token securely)
av.login()  # Google OAuth by default
# av.login(provider="github")  # Or GitHub OAuth

# Step 2: Create/manage API keys with JWT authentication
result = av.create_api_key(
    name="My App Key",
    description="Production API key for my recipe app",
    environment="production"
)
print(f"Created key: {result['key']['api_key']}")

# Step 3: Use nutrition API (automatically uses stored API key)
nutrition = av.analyze_ingredient("2 cups chocolate chips")
print(f"Calories: {nutrition.nutrition.calories_total}")
print(f"Protein: {nutrition.nutrition.protein_total}g")
print(f"USDA: {nutrition.usda_match.description}")
```

### 🔑 API Key Management

```python
# List all your API keys
keys = av.list_api_keys()
for key in keys['keys']:
    print(f"{key['key_name']}: {key['monthly_usage']}/{key['monthly_limit']}")

# Switch to different API key
av.switch_to_api_key("sk_prod_abc123...")

# Delete old keys
av.delete_api_key(key_id=123)
```

### 🚀 Alternative Methods

```python
# Method 1: Direct API key (if you already have one)
client = av.NutritionAPI(api_key="sk_starter_your_api_key_here")

# Method 2: Environment variable (for CI/CD)
# export AVOCAVO_API_KEY=sk_starter_your_api_key_here
result = av.analyze_ingredient("2 cups flour")
```

### 🔐 Secure Credential Management

The Python SDK uses a modern two-step authentication system:

1. **JWT Tokens**: For identity verification and API key management
2. **API Keys**: For actual nutrition API requests

All credentials are stored securely using your system's keyring:

- **macOS**: Stored in Keychain (same as Safari, Chrome)
- **Windows**: Stored in Credential Manager  
- **Linux**: Stored in Secret Service (gnome-keyring, kwallet)

```python
# One-time OAuth login - JWT token stored securely
av.login()  # Opens browser for Google OAuth

# Create API keys using JWT authentication
new_key = av.create_api_key(
    name="Production Key",
    environment="production"
)

# Use anywhere in your projects - API key automatically used
result = av.analyze_ingredient("1 cup quinoa")
print(f"✅ {result.nutrition.calories_total} calories")

# Check login status
user = av.get_current_user()
if user:
    print(f"Logged in as: {user['email']}")
    
# Logout and clear credentials  
av.logout()
```

### 🔑 Direct API Key (Legacy)

If you already have an API key, you can use it directly:

```python
from avocavo_nutrition import NutritionAPI

# Use existing API key directly
client = NutritionAPI(api_key="sk_starter_your_api_key_here")
result = client.analyze_ingredient("1 cup rice")
print(f"Calories: {result.nutrition.calories_total}")

# Or via environment variable
import os
os.environ['AVOCAVO_API_KEY'] = 'sk_starter_your_api_key_here'
result = av.analyze_ingredient("1 cup rice")  # Uses env var automatically
```

## 🎯 100% USDA Data

**All nutrition data comes from USDA FoodData Central** - the official U.S. government nutrition database. AI is used only for intelligent matching to find the best USDA food entry for your ingredient. No hallucination, no made-up data.

## ⚡ Any Input Format

**No rigid formatting required - describe ingredients any way you want:**

```python
# Descriptive ingredients
result = av.analyze_ingredient("2 tablespoons of extra virgin olive oil")

# Any style works
result = av.analyze_ingredient("I'm using about 1 cup of chicken breast, grilled")

# Precise or approximate
result = av.analyze_ingredient("100g brown rice, cooked")

# Include preparation details
result = av.analyze_ingredient("2 cups flour (all-purpose, for baking)")
```

**Bulletproof USDA matching with 94%+ cache hit rate and anti-hallucination protection.**

## 🎯 What You Can Do

### 🥘 Analyze Ingredients
```python
# Any ingredient with quantity - flexible input formats
result = av.analyze_ingredient("2 cups broccoli")
if result.success:
    # All 29 nutrition fields available
    print(f"Calories: {result.nutrition.calories}")  # 114.08
    print(f"Protein: {result.nutrition.protein}g")   # 9.46g
    print(f"Total Fat: {result.nutrition.total_fat}g")  # 1.25g
    print(f"Carbohydrates: {result.nutrition.carbohydrates}g")  # 23.07g
    print(f"Fiber: {result.nutrition.fiber}g")  # 8.83g
    print(f"Calcium: {result.nutrition.calcium}mg")  # 169.28mg
    print(f"Iron: {result.nutrition.iron}mg")  # 2.54mg
    
    # Null transparency - missing nutrients shown as None
    print(f"Vitamin C: {result.nutrition.vitamin_c}")  # None (not in USDA data)
    print(f"Folate: {result.nutrition.folate}")  # None (not in USDA data)
    
    # Enhanced metadata
    print(f"USDA Match: {result.metadata.usda_match.description}")  # "Broccoli, raw"
    print(f"FDC ID: {result.metadata.usda_match.fdc_id}")  # 747447
    print(f"Data Quality: {result.metadata.match_quality}")  # "excellent"
    print(f"Confidence: {result.metadata.confidence}")  # 0.95
    print(f"Estimated Grams: {result.parsing.estimated_grams}")  # 368g
    print(f"USDA Link: {result.metadata.usda_link}")

# Example with olive oil (previously returned 0 calories)
oil_result = av.analyze_ingredient("8 tablespoons olive oil")
print(f"Olive oil calories: {oil_result.nutrition.calories}")  # 990.08 (not 0!)
print(f"Selected USDA entry: {oil_result.metadata.usda_match.description}")  # "Oil, olive, salad or cooking"
print(f"Avoided corrupted entry: FDC {oil_result.metadata.usda_match.fdc_id}")  # 171413 (not 748608)
```

### 🍳 Analyze Complete Recipes
```python
# Full recipe with per-serving calculations
recipe = av.analyze_recipe([
    "2 cups all-purpose flour",
    "1 cup whole milk",
    "2 large eggs", 
    "1/4 cup sugar"
], servings=8)

print(f"Per serving: {recipe.nutrition.per_serving.calories} calories")
print(f"Total recipe: {recipe.nutrition.total.calories} calories")
```

### ⚡ Batch Processing
```python
# Analyze multiple ingredients efficiently
# Batch limits: Free Trial (3), Starter (8), Pro (50), Enterprise (100) ingredients
batch = av.analyze_batch([
    "1 cup quinoa",
    "2 tbsp olive oil", 
    "4 oz salmon",
    "1 cup spinach"
])

for item in batch.results:
    if item.success:
        print(f"{item.ingredient}: {item.nutrition.calories} cal")
```

### 📊 Account Management
```python
# Check your usage and limits
account = av.get_account_usage()
print(f"Plan: {account.plan_name}")
print(f"Usage: {account.usage.current_month}/{account.usage.monthly_limit}")
print(f"Remaining: {account.usage.remaining}")
```

## ✨ Bulletproof Features

### 🛡️ **Anti-Hallucination Protection**
- **Smart USDA Matching**: AI used only for intelligent matching to USDA database
- **Verified Database Search**: All matches verified against real USDA FoodData Central
- **Mathematical Calculation Only**: Nutrition = (USDA_per_100g × grams) ÷ 100
- **Zero AI Nutrition Data**: 100% database-sourced nutrition facts
- **Transparent Tier System**: Shows exactly how each ingredient was matched

### 🔄 **10-Layer Bulletproof Flow**
1. 🚀 **Redis Cache**: Instant exact match (sub-1ms)
2. 💾 **Supabase Cache**: Persistent exact match (1-5ms)
3. 🧠 **Intelligent Parsing**: Extract ingredient + quantity + unit
4. 📏 **Deterministic Conversion**: Unit → grams using conversion tables
5. 🎯 **SQL Exact Search**: Direct USDA database lookup
6. 🔍 **Fuzzy Match**: High-confidence fuzzy matching (90%+)
7. 🤖 **Smart USDA Matching**: Intelligent matching to USDA database
8. 🛡️ **Validated Search**: Verify all matches against USDA data
9. 🧮 **Mathematical Calculation**: Scale nutrition to actual quantity
10. 💾 **Multi-Tier Caching**: Store for future instant access

### 🎯 **Bulletproof USDA Accuracy**
- **Anti-hallucination protection**: AI never provides nutrition data
- Real FDC IDs from USDA FoodData Central
- **Mathematical calculations**: Handles missing calories (Protein×4 + Carbs×4 + Fat×9)
- **Smart zero-calorie detection** for ingredients like salt and water
- Verification URLs for manual checking
- **7-tier parsing system** shows exactly how each ingredient was matched
- **10-layer bulletproof flow** ensures 100% reliability

### ⚡ **Bulletproof Performance**
- **94%+ cache hit rate** = sub-second responses  
- **8,000+ requests/hour** throughput
- **Multi-tier caching**: Redis → Supabase → Local USDA
- **Anti-hallucination protection** with verified calculations
- **Mathematical calorie calculation** for missing nutrients

### 🔧 **Any Input Format**
- Handles "2 cups flour" or "1 lb chicken breast"
- Any ingredient description style
- Automatic quantity and measurement parsing
- No rigid formatting requirements

### 🛠️ **Developer Friendly**
- Secure credential storage with `keyring`
- Type hints and comprehensive error handling
- Works with environment variables
- Detailed documentation and examples

## 📊 Complete Nutrition Data (All 29 Fields)

```python
result = av.analyze_ingredient("1 cup cooked rice")
nutrition = result.nutrition

# Core macronutrients (always available)
print(f"Calories: {nutrition.calories}")
print(f"Protein: {nutrition.protein}g")
print(f"Total Fat: {nutrition.total_fat}g")
print(f"Carbohydrates: {nutrition.carbohydrates}g")
print(f"Fiber: {nutrition.fiber}g")
print(f"Sodium: {nutrition.sodium}mg")

# Detailed fats (may be None if not in USDA data)
print(f"Saturated Fat: {nutrition.saturated_fat}g")  # May be None
print(f"Cholesterol: {nutrition.cholesterol}mg")     # May be None
print(f"Sugar: {nutrition.sugar}g")                  # May be None
print(f"Trans Fat: {nutrition.trans_fat}g")          # May be None
print(f"Monounsaturated Fat: {nutrition.monounsaturated_fat}g")  # May be None
print(f"Polyunsaturated Fat: {nutrition.polyunsaturated_fat}g")  # May be None

# Major minerals (may be None if not in USDA data)
print(f"Calcium: {nutrition.calcium}mg")     # May be None
print(f"Iron: {nutrition.iron}mg")           # May be None
print(f"Potassium: {nutrition.potassium}mg") # May be None
print(f"Magnesium: {nutrition.magnesium}mg") # May be None
print(f"Phosphorus: {nutrition.phosphorus}mg") # May be None
print(f"Zinc: {nutrition.zinc}mg")           # May be None
print(f"Selenium: {nutrition.selenium}mcg")  # May be None

# Vitamins (may be None if not in USDA data)
print(f"Vitamin A: {nutrition.vitamin_a}IU")     # May be None
print(f"Vitamin C: {nutrition.vitamin_c}mg")     # May be None
print(f"Vitamin E: {nutrition.vitamin_e}mg")     # May be None
print(f"Vitamin K: {nutrition.vitamin_k}mcg")    # May be None
print(f"Vitamin D: {nutrition.vitamin_d_iu}IU")  # May be None

# B-Complex vitamins (may be None if not in USDA data)
print(f"Thiamin (B1): {nutrition.thiamin}mg")    # May be None
print(f"Riboflavin (B2): {nutrition.riboflavin}mg") # May be None
print(f"Niacin (B3): {nutrition.niacin}mg")      # May be None
print(f"Vitamin B6: {nutrition.vitamin_b6}mg")   # May be None
print(f"Folate: {nutrition.folate}mcg")          # May be None
print(f"Vitamin B12: {nutrition.vitamin_b12}mcg") # May be None

# Transparency: None means not available in USDA data, not zero
if nutrition.vitamin_c is None:
    print("ℹ️  Vitamin C data not available in USDA database for this food")
```

## 💰 Pricing Plans

| Plan | Monthly Calls | Price | Batch Limit | Features |
|------|---------------|-------|-------------|----------|
| **Free Trial** | 500 | **Free** | 3 ingredients | One-time trial credit, full feature access |
| **Starter** | 3,000 | $9/month | 8 ingredients | Perfect for indie developers and small projects |
| **Pro** | 20,000 | $49/month | 25 ingredients | Production apps, advanced batch processing |
| **Enterprise** | 100,000 | $199/month | 50 ingredients | High volume, maximum batch capability |

### Pay-As-You-Go Credits
Need more calls? Purchase credits anytime:
- **$3** = 1,000 additional calls (batch limit: 5 ingredients)
- **$30** = 5,000 additional calls  
- **$10** = 10,000 additional calls
- **$25** = 25,000 additional calls
- **$50** = 50,000 additional calls
- **$100** = 100,000 additional calls

Credits never expire and work with any plan!
- **$100** = 100,000 additional calls

Credits never expire and work with any plan!

[**Get your API key →**](https://nutrition.avocavo.app)

## 🔐 Authentication Options

### Option 1: Login (Recommended)
```python
import avocavo_nutrition as av

# Login once, use everywhere
av.login("user@example.com", "password")

# Credentials stored securely with keyring
result = av.analyze_ingredient("1 cup rice")
```

### Option 2: API Key
```python
from avocavo_nutrition import NutritionAPI

# Direct API key usage
client = NutritionAPI(api_key="your_api_key")
result = client.analyze_ingredient("1 cup rice")
```

### Option 3: Environment Variable
```bash
export AVOCAVO_API_KEY="your_api_key_here"
```

```python
import avocavo_nutrition as av
# API key automatically detected from environment
result = av.analyze_ingredient("1 cup rice")
```

## 🏗️ Real-World Examples

### Recipe App Integration
```python
import avocavo_nutrition as av

def calculate_recipe_nutrition(ingredients, servings=1):
    """Calculate nutrition for any recipe"""
    recipe = av.analyze_recipe(ingredients, servings)
    
    if recipe.success:
        return {
            'calories_per_serving': recipe.nutrition.per_serving.calories,
            'protein_per_serving': recipe.nutrition.per_serving.protein,
            'total_calories': recipe.nutrition.total.calories,
            'usda_verified_ingredients': recipe.usda_matches
        }
    else:
        return {'error': recipe.error}

# Usage
recipe_nutrition = calculate_recipe_nutrition([
    "2 cups flour",
    "1 cup milk", 
    "2 eggs"
], servings=6)
```

### Fitness Tracker Integration  
```python
def track_daily_nutrition(food_entries):
    """Track daily nutrition from food entries"""
    total_nutrition = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0
    }
    
    for food in food_entries:
        result = av.analyze_ingredient(food)
        if result.success:
            total_nutrition['calories'] += result.nutrition.calories
            total_nutrition['protein'] += result.nutrition.protein
            total_nutrition['carbs'] += result.nutrition.carbs
            total_nutrition['fat'] += result.nutrition.fat
    
    return total_nutrition

# Usage
daily_foods = [
    "1 cup oatmeal",
    "1 medium banana", 
    "6 oz grilled chicken",
    "2 cups steamed broccoli"
]
daily_totals = track_daily_nutrition(daily_foods)
```

### Restaurant Menu Analysis
```python
def analyze_menu_item(ingredients):
    """Analyze nutrition for restaurant menu items"""
    # Use batch processing for efficiency
    # Batch limits: Free (5), Starter (10), Professional (20), Enterprise (50+) ingredients  
    batch = av.analyze_batch(ingredients)
    
    total_calories = sum(
        item.nutrition.calories 
        for item in batch.results 
        if item.success
    )
    
    return {
        'total_calories': total_calories,
        'success_rate': batch.success_rate,
        'ingredients_analyzed': batch.successful_matches
    }
```

## 🛠️ Advanced Usage

### Error Handling
```python
from avocavo_nutrition import ApiError, RateLimitError, AuthenticationError

try:
    result = av.analyze_ingredient("mystery ingredient")
    if result.success:
        print(f"Found: {result.usda_match.description}")
    else:
        print(f"No match: {result.error}")
        
except RateLimitError as e:
    print(f"Rate limit exceeded. Limit: {e.limit}, Usage: {e.usage}")
except AuthenticationError as e:
    print(f"Auth error: {e.message}")
except ApiError as e:
    print(f"API Error: {e.message}")
```

### Configuration
```python
# Use development environment
client = NutritionAPI(
    api_key="your_key",
    base_url="https://devapp.avocavo.app",  # Dev environment
    timeout=60  # Custom timeout
)

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")
print(f"Cache Hit Rate: {health['cache']['hit_rate']}")
```

### User Management
```python
# Check login status
if av.is_logged_in():
    user = av.get_current_user()
    print(f"Logged in as: {user['email']}")
else:
    print("Please login: av.login()")  # OAuth browser login

# Login with different provider
av.login(provider="github")  # GitHub OAuth instead of Google

# Logout
result = av.logout()
print(result['message'])  # "Successfully logged out"
```

## 🔍 What Information You Get

The Avocavo Nutrition API provides comprehensive nutrition data with USDA verification:

### Core Nutrition Facts
- **Calories** - Energy content
- **Macronutrients** - Protein, carbohydrates, total fat
- **Fiber & Sugar** - Detailed carbohydrate breakdown  
- **Minerals** - Sodium, calcium, iron
- **Fats** - Saturated fat, cholesterol

### USDA Verification
- **Real FDC IDs** from USDA FoodData Central
- **Verification URLs** for manual checking
- **Data source types** (Foundation, SR Legacy, Survey, Branded)
- **Confidence scores** for match quality

### Bulletproof System Metrics
- **Cache layer hit** - Which cache tier provided the data
- **Processing method** - Exact path through bulletproof flow
- **Anti-hallucination status** - Verification that no AI nutrition data was used
- **Mathematical verification** - Confirmation of calculated vs database nutrition
- **Response times** - Sub-second bulletproof performance tracking

### Complete API Response Fields
```python
result = av.analyze_ingredient("1 cup cooked brown rice")

# Core nutrition data (100% mathematical calculation)
print(f"Calories: {result.nutrition.calories}")           # 216.0
print(f"Protein: {result.nutrition.protein}g")            # 5.0
print(f"Carbs: {result.nutrition.carbs}g")               # 45.0
print(f"Fiber: {result.nutrition.fiber}g")               # 3.5
print(f"Calcium: {result.nutrition.calcium_total}mg")     # 23.0
print(f"Iron: {result.nutrition.iron_total}mg")          # 0.8

# USDA verification (bulletproof source)
print(f"FDC ID: {result.usda_match.fdc_id}")             # 168880
print(f"Description: {result.usda_match.description}")    # "Rice, brown, long-grain, cooked"
print(f"Data Type: {result.usda_match.data_type}")       # "foundation_food"
print(f"Verify: {result.verification_url}")              # USDA verification link

# System performance & caching
print(f"From Cache: {result.from_cache}")                # True/False
print(f"Cache Type: {result.cache_type}")                # "redis" | "supabase" | None
print(f"Processing Time: {result.processing_time_ms}ms")  # 15.2 (bulletproof speed)
print(f"Method Used: {result.method_used}")              # "llm_driven_search" | "sql_exact" | "fuzzy_match"

# Parsing details
print(f"Estimated Grams: {result.estimated_grams}")      # 195.0
print(f"Parsed Name: {result.ingredient_name}")          # "1 cup cooked brown rice"
```

## Recipe Results with Individual Ingredient Details
```python
recipe = av.analyze_recipe([
    "2 cups all-purpose flour", 
    "1 cup whole milk"
], servings=4)

# Recipe-level data
print(f"Total Calories: {recipe.nutrition.total.calories}")      # 1862.21
print(f"Per Serving: {recipe.nutrition.per_serving.calories}")   # 465.55
print(f"USDA Matches: {recipe.usda_matches}")                   # 2
print(f"Processing Time: {recipe.processing_time_ms}ms")         # 5.3
# Note: All nutrition data is USDA-verifiable via included FDC IDs and verification URLs

# Individual ingredient details
for ingredient in recipe.nutrition.ingredients:
    print(f"Ingredient: {ingredient.ingredient}")
    print(f"  Calories: {ingredient.nutrition.calories}")
    print(f"  USDA: {ingredient.usda_match.description}")
    print(f"  Verify: {ingredient.verification_url}")
```

## 📚 Documentation

- **[Complete API Documentation](https://nutrition.avocavo.app/docs/python)** - Full reference
- **[Get API Key](https://nutrition.avocavo.app)** - Sign up for free
- **[GitHub Repository](https://github.com/avocavo/nutrition-api-python)** - Source code
- **[Support](mailto:api-support@avocavo.com)** - Get help

## 🤝 Support

- **Email**: [api-support@avocavo.com](mailto:api-support@avocavo.com)
- **Documentation**: [nutrition.avocavo.app/docs/python](https://nutrition.avocavo.app/docs/python)
- **Status Page**: [status.avocavo.app](https://status.avocavo.app)
- **Feature Requests**: [GitHub Issues](https://github.com/avocavo/nutrition-api-python/issues)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by the Avocavo team**

*Get started in 30 seconds: `pip install avocavo-nutrition`*