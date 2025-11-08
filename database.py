import asyncpg
import config
from datetime import datetime
from typing import Optional

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize connection pool - called once on startup"""
        if not config.SUPABASE_DB_URL:
            raise ValueError("SUPABASE_DB_URL not set in config.py")
        
        # Create connection pool with Supabase settings
        self.pool = await asyncpg.create_pool(
            config.SUPABASE_DB_URL,
            min_size=1,
            max_size=10,
            ssl="require",              # Required for Supabase
            command_timeout=60,
            server_settings={'application_name': 'campus_delivery_bot'}
        )
        
        await self._create_tables()
        print("✅ Database connected to Supabase and tables ready")
    
    async def _create_tables(self):
        """Create tables if they don't exist"""
        async with self.pool.acquire() as conn:
            # Enable UUID extension
            await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            
            # Users table (stores authorized users and balances)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    name TEXT NOT NULL,
                    balance DECIMAL(10,2) DEFAULT 0.00,
                    user_type TEXT,  -- 'contract_user' or 'single_user'
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Orders table (stores all orders)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id),
                    order_number TEXT UNIQUE NOT NULL,
                    cafe TEXT NOT NULL,
                    name TEXT NOT NULL,
                    gender CHAR(1) CHECK (gender IN ('M', 'F')),
                    phone TEXT NOT NULL,
                    time TEXT NOT NULL,
                    food TEXT NOT NULL,
                    place TEXT NOT NULL,
                    total_items INTEGER NOT NULL,
                    total_price DECIMAL(10,2) NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Index for performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_telegram_status 
                ON orders(telegram_id, status);
            """)
    
    async def close(self):
        """Close connection pool on shutdown"""
        if self.pool:
            await self.pool.close()
    
    # =================== USER METHODS ===================
    
    async def is_user_authorized(self, telegram_id: int) -> bool:
        """Check if user exists in database"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT 1 FROM users WHERE telegram_id = $1", 
                telegram_id
            )
            return result is not None
    
    async def get_user_balance(self, telegram_id: int) -> float:
        """Get user balance from database"""
        async with self.pool.acquire() as conn:
            balance = await conn.fetchval(
                "SELECT balance FROM users WHERE telegram_id = $1",
                telegram_id
            )
            return float(balance) if balance else 0.0
    
    async def update_user_balance(self, telegram_id: int, new_balance: float):
        """Update user balance in database"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET balance = $1 WHERE telegram_id = $2",
                new_balance, telegram_id
            )
    
    async def add_user(self, telegram_id: int, name: str, initial_balance: float) -> tuple[bool, str]:
        """Add new user (admin command)"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO users (telegram_id, name, balance) VALUES ($1, $2, $3)",
                    telegram_id, name, initial_balance
                )
                return True, "User added successfully"
        except asyncpg.exceptions.UniqueViolationError:
            return False, "User already exists"
        except Exception as e:
            return False, str(e)
    
    # =================== ORDER METHODS ===================
    
    async def get_next_order_number(self) -> str:
        """Generate sequential order number"""
        async with self.pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM orders")
            return f"ORD-{count + 1:06d}"
    
    async def create_order(self, order_data: dict):
        """Save order to Supabase"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO orders (
                    telegram_id, order_number, cafe, name, gender, phone,
                    time, food, place, total_items, total_price
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
                order_data['user_telegram_id'],
                order_data['order_number'],
                order_data['cafe'],
                order_data['name'],
                order_data['gender'],
                order_data['phone'],
                order_data['time'],
                order_data['food'],
                order_data['place'],
                order_data['total_items'],
                order_data['total_price']
            )