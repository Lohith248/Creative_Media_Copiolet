# 📚 Campaign History Database (Supabase Cloud)

## Overview

The Creative Media Co-Pilot now saves **ALL generated campaigns** to a **Supabase cloud database**, so you can:

✅ **View past campaigns** - See all your previous posts from anywhere  
✅ **Track quality trends** - Monitor your campaign performance  
✅ **Search campaigns** - Find campaigns by product name or goal  
✅ **Reuse successful content** - Learn what worked best  
✅ **Real-time sync** - Instant updates across devices  
✅ **Production-ready** - PostgreSQL database, not toy storage  

---

## Why Supabase?

🌟 **Cloud-Native** - Data persists across devices and sessions  
🌟 **Real-time** - See campaigns appear instantly as they're created  
🌟 **Scalable** - PostgreSQL handles millions of rows  
🌟 **Professional** - Same tech used by Netflix, Uber, etc.  
🌟 **Free Tier** - 500MB database, 2GB bandwidth/month  
🌟 **Auto API** - REST and GraphQL endpoints included  
🌟 **Dashboard** - View/edit data in beautiful web UI  

**This is production-grade architecture, not a hackathon toy!**

---

## Database Features

### **1. Automatic Saving**
Every campaign you generate is automatically saved with:
- Product name, platform, goal, audience
- Generated copy and hashtags
- Image file path
- Quality scores (overall, brand, compliance, readability, engagement)
- Iteration count
- Research data (if included)
- Timestamp

### **2. Campaign History Tab (Tab 6)**
Access your campaign history in the new **"📚 Campaign History"** tab:

**Features:**
- 📊 **Overall Statistics** - Total campaigns, average quality, approval rate
- 🔍 **Search** - Find campaigns by product name or objective
- 📋 **Campaign List** - View recent 20 campaigns with key metrics
- 👁️ **View Details** - See full campaign details including:
  - Generated copy
  - Hashtags
  - Quality scores
  - Process information (iterations, research included)
  - Generated image

### **3. Search & Filter**
- Search by product name: "Water Bottle"
- Search by objective: "Brand awareness"
- Sort by date (newest first)

---

## Database Structure

### Supabase PostgreSQL Table:

**campaigns** - Main campaign data
```sql
- id (BIGSERIAL PRIMARY KEY)
- product_name (TEXT)
- platform (TEXT)
- brand_preset (TEXT)
- objective (TEXT)
- target_audience (TEXT)
- final_copy (TEXT)
- hashtags (TEXT)
- image_path (TEXT)
- quality_score (DECIMAL)
- brand_score (INTEGER)
- compliance_score (INTEGER)
- readability_score (DECIMAL)
- engagement_score (DECIMAL)
- iteration_count (INTEGER)
- status (TEXT)
- research_included (BOOLEAN)
- research_data (JSONB)
- created_at (TIMESTAMP WITH TIME ZONE)
- updated_at (TIMESTAMP WITH TIME ZONE)
```

**Indexes for Performance:**
- `idx_campaigns_created_at` - Fast sorting by date
- `idx_campaigns_product_name` - Fast product search
- `idx_campaigns_platform` - Platform filtering

---

## Database Location

**Type:** Supabase (PostgreSQL in the cloud)

**Access:**
- Via Gradio UI (Tab 6)
- Via Supabase Dashboard (https://app.supabase.com)
- Via REST API (auto-generated)
- Via GraphQL (auto-generated)

**Portability:** Export to CSV/JSON from Supabase dashboard

---

## Usage Examples

### View Recent Campaigns
1. Open **Tab 6: Campaign History**
2. Click **🔄 Refresh** to load campaigns
3. See list with Product, Platform, Quality Score, Date

### Search Campaigns
1. Enter search term (e.g., "Eco-Friendly")
2. Click **🔍 Search**
3. Results filtered by product name or objective

### View Campaign Details
1. Note the **Campaign ID** from the list
2. Enter ID in "Campaign ID to View"
3. Click **👁️ View Details**
4. See full campaign details + generated image

---

## Statistics Tracked

- **Total Campaigns**: Number of campaigns generated
- **Average Quality**: Mean quality score across all campaigns
- **Average Brand Score**: Mean brand alignment percentage
- **Approved Count**: Campaigns that passed all validations

---

## Benefits for Hackathon Demo

✅ **Cloud-Hosted** - Judges can access from anywhere  
✅ **Real-time Sync** - Show instant updates across browsers  
✅ **Professional Architecture** - Production-grade PostgreSQL  
✅ **Persistent Data** - Survives restarts, demos multiple campaigns  
✅ **Impressive Tech Stack** - Shows you know modern cloud architecture  
✅ **Auto API** - REST/GraphQL endpoints included  
✅ **Scalable** - Not a toy database, ready for real users  

**Demo Script for Judges:**
1. Generate campaign in Browser A → Tab 1
2. Open Browser B → Tab 6 → **Data appears instantly!**
3. Show Supabase dashboard → **Same data in beautiful UI!**
4. Say: *"This is the same cloud database architecture used by companies like Netflix"*

🎯 **That's production-ready, not a hackathon hack!**

---

## Future Enhancements (Post-Hackathon)

Potential features for production:
- User authentication (Supabase Auth built-in!)
- Team collaboration (multi-user access)
- Export campaigns to CSV/JSON/PDF
- Campaign comparison tool
- Quality trend graphs and analytics
- A/B testing analytics
- Tag system for organization
- Campaign versioning
- Bulk operations (delete, export, duplicate)
- API webhooks for integrations
- Real-time notifications

All easily implemented with Supabase features!

---

## Technical Details

**Database Engine:** Supabase (PostgreSQL 15)  
**Connection:** Official Supabase Python client  
**Authentication:** API key (anon public key)  
**Security:** Row Level Security (RLS) enabled  
**Backups:** Automatic daily backups (paid plans)  
**Scaling:** Auto-scaling, handles millions of rows  
**Latency:** <100ms globally via CDN  

---

## Setup

**See:** `docs/SUPABASE_SETUP.md` for complete setup guide

**Quick Start:**
1. Create Supabase account (2 min)
2. Create project (3 min)
3. Run SQL to create table (1 min)
4. Add credentials to .env (1 min)
5. Install: `pip install supabase` (1 min)
6. Test: `python src/database/supabase_db.py` (1 min)

**Total: ~10 minutes** ⚡

---

## Testing

Run the database test:
```bash
python src/database/supabase_db.py
```

This will:
1. Connect to Supabase
2. Create test campaign
3. Query recent campaigns
4. Display statistics
5. Confirm cloud sync

---

## Troubleshooting

**Issue:** "Not connected to Supabase"  
**Solution:** Check `.env` has SUPABASE_URL and SUPABASE_KEY

**Issue:** "Table does not exist"  
**Solution:** Run CREATE TABLE SQL in Supabase dashboard

**Issue:** Campaign not appearing  
**Solution:** Click 🔄 Refresh in Tab 6, check Supabase dashboard

**Issue:** Image not loading  
**Solution:** Check image file still exists at path (images are local, not cloud)

---

**Database automatically initialized on first run!** 🎉

Just set up Supabase credentials and generate campaigns - history tracked automatically in the cloud!
