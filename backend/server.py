from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
import base64
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===================== MODELS =====================

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Product Models
class ProductCategory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    image_url: str
    description: str
    design_zones: List[Dict[str, Any]]  # [{name, x, y, width, height}]

class DesignUpload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    image_data: str  # base64
    category: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DesignUploadCreate(BaseModel):
    name: str
    image_data: str
    category: str

# Color Palette Models
class ColorPalette(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    colors: List[str]
    category: str

class Pattern(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    svg_data: str
    category: str
    colors: List[str]

# Fashion Trend Models
class FashionTrend(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    data: Dict[str, Any]
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrendUpload(BaseModel):
    data: Dict[str, Any]

# Chat Models
class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # user or assistant
    content: str
    model: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    session_id: str
    message: str
    model: str  # openai, claude, gemini
    context: Optional[str] = None

# ===================== INITIAL DATA =====================

PRODUCT_CATEGORIES = [
    {
        "id": "tshirt",
        "name": "T-Shirt",
        "slug": "tshirt",
        "image_url": "https://images.unsplash.com/photo-1722310752951-4d459d28c678",
        "description": "Classic cotton t-shirt",
        "design_zones": [
            {"name": "Front Center", "x": 35, "y": 25, "width": 30, "height": 35},
            {"name": "Left Chest", "x": 55, "y": 20, "width": 15, "height": 12},
            {"name": "Back Center", "x": 35, "y": 25, "width": 30, "height": 35}
        ]
    },
    {
        "id": "hoodie",
        "name": "Hoodie",
        "slug": "hoodie",
        "image_url": "https://images.unsplash.com/photo-1622024773918-d59feb56ca32",
        "description": "Comfortable pullover hoodie",
        "design_zones": [
            {"name": "Front Center", "x": 30, "y": 30, "width": 35, "height": 30},
            {"name": "Kangaroo Pocket", "x": 30, "y": 60, "width": 35, "height": 15},
            {"name": "Back Full", "x": 25, "y": 20, "width": 50, "height": 50}
        ]
    },
    {
        "id": "cap",
        "name": "Cap",
        "slug": "cap",
        "image_url": "https://images.unsplash.com/photo-1691256676359-20e5c6d4bc92",
        "description": "Snapback cap",
        "design_zones": [
            {"name": "Front Panel", "x": 25, "y": 30, "width": 50, "height": 30},
            {"name": "Side Panel", "x": 10, "y": 35, "width": 20, "height": 25}
        ]
    },
    {
        "id": "mug",
        "name": "Mug",
        "slug": "mug",
        "image_url": "https://images.unsplash.com/photo-1580485978276-08f3452221a7",
        "description": "Ceramic coffee mug",
        "design_zones": [
            {"name": "Wrap Around", "x": 10, "y": 20, "width": 60, "height": 50}
        ]
    },
    {
        "id": "tote-bag",
        "name": "Tote Bag",
        "slug": "tote-bag",
        "image_url": "https://images.unsplash.com/photo-1746399565180-0dfbfba51c2b",
        "description": "Canvas tote bag",
        "design_zones": [
            {"name": "Front Center", "x": 20, "y": 25, "width": 60, "height": 50}
        ]
    },
    {
        "id": "sneakers",
        "name": "Sneakers",
        "slug": "sneakers",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        "description": "Athletic sneakers",
        "design_zones": [
            {"name": "Side Panel", "x": 20, "y": 30, "width": 60, "height": 35},
            {"name": "Tongue", "x": 40, "y": 10, "width": 20, "height": 20},
            {"name": "Heel Tab", "x": 75, "y": 40, "width": 15, "height": 15}
        ]
    },
    {
        "id": "phone-case",
        "name": "Phone Case",
        "slug": "phone-case",
        "image_url": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb",
        "description": "Smartphone protective case",
        "design_zones": [
            {"name": "Full Back", "x": 10, "y": 10, "width": 80, "height": 80}
        ]
    },
    {
        "id": "backpack",
        "name": "Backpack",
        "slug": "backpack",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
        "description": "Everyday backpack",
        "design_zones": [
            {"name": "Front Pocket", "x": 25, "y": 50, "width": 50, "height": 30},
            {"name": "Main Panel", "x": 20, "y": 15, "width": 60, "height": 35}
        ]
    }
]

COLOR_PALETTES = [
    {"id": "vibrant", "name": "Vibrant Pop", "colors": ["#FF0099", "#CCFF00", "#00FFFF", "#9D00FF", "#FF6600"], "category": "bold"},
    {"id": "earth", "name": "Earth Tones", "colors": ["#8B4513", "#DEB887", "#556B2F", "#D2691E", "#F5DEB3"], "category": "natural"},
    {"id": "neon", "name": "Neon Nights", "colors": ["#FF00FF", "#00FF00", "#FF0000", "#0000FF", "#FFFF00"], "category": "bold"},
    {"id": "pastel", "name": "Soft Pastels", "colors": ["#FFB6C1", "#B0E0E6", "#98FB98", "#DDA0DD", "#FAFAD2"], "category": "soft"},
    {"id": "monochrome", "name": "Monochrome", "colors": ["#000000", "#333333", "#666666", "#999999", "#CCCCCC"], "category": "classic"},
    {"id": "ocean", "name": "Ocean Breeze", "colors": ["#006994", "#40E0D0", "#0077BE", "#20B2AA", "#5F9EA0"], "category": "cool"},
    {"id": "sunset", "name": "Sunset Glow", "colors": ["#FF4500", "#FF6347", "#FF7F50", "#FFD700", "#FFA07A"], "category": "warm"},
    {"id": "forest", "name": "Forest Walk", "colors": ["#228B22", "#2E8B57", "#6B8E23", "#8FBC8F", "#90EE90"], "category": "natural"},
    {"id": "retro", "name": "Retro 80s", "colors": ["#FF1493", "#00CED1", "#FF4500", "#7B68EE", "#32CD32"], "category": "bold"},
    {"id": "minimalist", "name": "Minimalist", "colors": ["#FFFFFF", "#F5F5F5", "#E0E0E0", "#BDBDBD", "#000000"], "category": "classic"}
]

PATTERNS = [
    {"id": "stripes", "name": "Bold Stripes", "category": "geometric", "colors": ["#000000", "#FFFFFF"]},
    {"id": "polka", "name": "Polka Dots", "category": "playful", "colors": ["#FF0099", "#FFFFFF"]},
    {"id": "chevron", "name": "Chevron", "category": "geometric", "colors": ["#CCFF00", "#000000"]},
    {"id": "abstract", "name": "Abstract Waves", "category": "artistic", "colors": ["#00FFFF", "#9D00FF"]},
    {"id": "grid", "name": "Grid Pattern", "category": "geometric", "colors": ["#000000", "#FFFFFF"]},
    {"id": "floral", "name": "Modern Floral", "category": "organic", "colors": ["#FF0099", "#CCFF00", "#000000"]},
    {"id": "camo", "name": "Urban Camo", "category": "streetwear", "colors": ["#333333", "#666666", "#999999"]},
    {"id": "tribal", "name": "Tribal Motifs", "category": "cultural", "colors": ["#8B4513", "#DEB887", "#000000"]},
    {"id": "splatter", "name": "Paint Splatter", "category": "artistic", "colors": ["#FF0099", "#CCFF00", "#00FFFF"]},
    {"id": "circuit", "name": "Circuit Board", "category": "tech", "colors": ["#00FF00", "#000000"]}
]

# Popular Design Research Data
POPULAR_DESIGN_ZONES = {
    "tshirt": {
        "research": "Based on bestselling designs from Nike, Supreme, Off-White",
        "hot_zones": [
            {"name": "Center Chest", "popularity": 85, "tip": "Large graphic prints perform best"},
            {"name": "Left Chest", "popularity": 70, "tip": "Small logos, brand emblems"},
            {"name": "Back Full", "popularity": 60, "tip": "Statement pieces, tour graphics"}
        ]
    },
    "hoodie": {
        "research": "Based on bestselling designs from Champion, Yeezy, Essentials",
        "hot_zones": [
            {"name": "Center Chest", "popularity": 80, "tip": "Bold text, minimal graphics"},
            {"name": "Back Oversize", "popularity": 75, "tip": "Large scale artwork"},
            {"name": "Hood", "popularity": 40, "tip": "Small embroidered details"}
        ]
    },
    "sneakers": {
        "research": "Based on bestselling designs from Nike, Adidas, New Balance",
        "hot_zones": [
            {"name": "Side Panel", "popularity": 90, "tip": "Swoosh-style branding"},
            {"name": "Tongue", "popularity": 75, "tip": "Brand logo placement"},
            {"name": "Heel Tab", "popularity": 65, "tip": "Signature detail spot"}
        ]
    },
    "cap": {
        "research": "Based on bestselling designs from New Era, 47 Brand",
        "hot_zones": [
            {"name": "Front Panel", "popularity": 95, "tip": "Primary logo placement"},
            {"name": "Side Panel", "popularity": 50, "tip": "Secondary branding"}
        ]
    }
}

# ===================== ROUTES =====================

@api_router.get("/")
async def root():
    return {"message": "Design Studio API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# Product Routes
@api_router.get("/products")
async def get_products():
    return PRODUCT_CATEGORIES

@api_router.get("/products/{slug}")
async def get_product(slug: str):
    for product in PRODUCT_CATEGORIES:
        if product["slug"] == slug:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@api_router.get("/products/{slug}/design-zones")
async def get_design_zones(slug: str):
    for product in PRODUCT_CATEGORIES:
        if product["slug"] == slug:
            research = POPULAR_DESIGN_ZONES.get(slug, {
                "research": "General design guidelines",
                "hot_zones": product["design_zones"]
            })
            return research
    raise HTTPException(status_code=404, detail="Product not found")

# Design Routes
@api_router.post("/designs")
async def upload_design(design: DesignUploadCreate):
    design_obj = DesignUpload(**design.model_dump())
    doc = design_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.designs.insert_one(doc)
    return {"id": design_obj.id, "message": "Design uploaded successfully"}

@api_router.get("/designs")
async def get_designs():
    designs = await db.designs.find({}, {"_id": 0}).to_list(100)
    return designs

@api_router.delete("/designs/{design_id}")
async def delete_design(design_id: str):
    result = await db.designs.delete_one({"id": design_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Design not found")
    return {"message": "Design deleted"}

# Color Palette Routes
@api_router.get("/palettes")
async def get_palettes():
    return COLOR_PALETTES

@api_router.get("/palettes/{category}")
async def get_palettes_by_category(category: str):
    return [p for p in COLOR_PALETTES if p["category"] == category]

# Pattern Routes
@api_router.get("/patterns")
async def get_patterns():
    return PATTERNS

# Fashion Trend Routes
@api_router.post("/trends")
async def upload_trends(trend: TrendUpload):
    trend_obj = FashionTrend(data=trend.data)
    doc = trend_obj.model_dump()
    doc['uploaded_at'] = doc['uploaded_at'].isoformat()
    await db.trends.insert_one(doc)
    return {"id": trend_obj.id, "message": "Trends uploaded successfully"}

@api_router.get("/trends")
async def get_trends():
    trends = await db.trends.find({}, {"_id": 0}).sort("uploaded_at", -1).to_list(10)
    return trends

@api_router.get("/trends/latest")
async def get_latest_trend():
    trend = await db.trends.find_one({}, {"_id": 0}, sort=[("uploaded_at", -1)])
    return trend or {}

# AI Chat Routes
FASHION_SYSTEM_PROMPT = """You are an expert AI Fashion Advisor - a trendsetter with the vision of Calvin Klein and the innovation of Nike's design team. You help users create stunning, marketable designs for their products.

Your expertise includes:
- Current fashion trends and forecasting
- Color theory and palette combinations
- Design placement and visual hierarchy
- Brand identity and market positioning
- Streetwear, luxury, and contemporary aesthetics

You provide:
- Constructive feedback on user designs
- Color and pattern recommendations
- Placement suggestions for maximum impact
- Market insights and trend analysis
- Creative direction while respecting the user's final decision

Always be encouraging yet honest. Give specific, actionable advice. Reference real fashion examples when relevant."""

@api_router.post("/chat")
async def chat_with_advisor(request: ChatRequest):
    api_key = os.environ.get('EMERGENT_LLM_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    # Get chat history for context
    history = await db.chat_history.find(
        {"session_id": request.session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(20)
    
    # Get latest trends for context
    latest_trend = await db.trends.find_one({}, {"_id": 0}, sort=[("uploaded_at", -1)])
    trend_context = ""
    if latest_trend:
        trend_context = f"\n\nLatest fashion trends data: {latest_trend.get('data', {})}"
    
    # Build system message with trend context
    system_message = FASHION_SYSTEM_PROMPT + trend_context
    if request.context:
        system_message += f"\n\nCurrent design context: {request.context}"
    
    # Initialize chat
    chat = LlmChat(
        api_key=api_key,
        session_id=request.session_id,
        system_message=system_message
    )
    
    # Configure model
    if request.model == "openai":
        chat.with_model("openai", "gpt-5.2")
    elif request.model == "claude":
        chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
    elif request.model == "gemini":
        chat.with_model("gemini", "gemini-3-flash-preview")
    else:
        chat.with_model("openai", "gpt-5.2")
    
    # Build message with history context
    history_text = ""
    if history:
        recent_history = history[-10:]  # Last 10 messages
        for msg in recent_history:
            history_text += f"{msg['role'].upper()}: {msg['content']}\n"
    
    full_message = request.message
    if history_text:
        full_message = f"Previous conversation:\n{history_text}\n\nUser's new message: {request.message}"
    
    user_message = UserMessage(text=full_message)
    
    try:
        response = await chat.send_message(user_message)
        
        # Save user message
        user_msg = ChatMessage(
            session_id=request.session_id,
            role="user",
            content=request.message,
            model=request.model
        )
        user_doc = user_msg.model_dump()
        user_doc['timestamp'] = user_doc['timestamp'].isoformat()
        await db.chat_history.insert_one(user_doc)
        
        # Save assistant response
        assistant_msg = ChatMessage(
            session_id=request.session_id,
            role="assistant",
            content=response,
            model=request.model
        )
        assistant_doc = assistant_msg.model_dump()
        assistant_doc['timestamp'] = assistant_doc['timestamp'].isoformat()
        await db.chat_history.insert_one(assistant_doc)
        
        return {"response": response, "model": request.model}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@api_router.get("/chat/{session_id}")
async def get_chat_history(session_id: str):
    history = await db.chat_history.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(100)
    return history

@api_router.delete("/chat/{session_id}")
async def clear_chat_history(session_id: str):
    await db.chat_history.delete_many({"session_id": session_id})
    return {"message": "Chat history cleared"}

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
