#!/usr/bin/env python3
"""
半自动订阅状态机
从"纯人工"升级到"半自动"：用户付款 → 上传凭证 → 人工一键确认 → 自动开通
"""

import sqlite3
from datetime import datetime, timedelta
from enum import Enum

DB_PATH = "/home/daministrator/.openclaw/workspace/openclaw-income-factory/data/tender_radar.db"

class SubscriptionStatus(Enum):
    """订阅状态"""
    TRIAL = "trial"  # 试用期
    ACTIVE = "active"  # 正常付费
    EXPIRED = "expired"  # 已过期
    CANCELLED = "cancelled"  # 已取消

class PaymentStatus(Enum):
    """支付状态"""
    PENDING = "pending"  # 待付款
    PAID_UNCONFIRMED = "paid_unconfirmed"  # 已付款待确认
    CONFIRMED = "confirmed"  # 已确认
    ACTIVE = "active"  # 服务开通
    EXPIRED = "expired"  # 已过期
    REFUNDED = "refunded"  # 已退款

class SubscriptionManager:
    """订阅管理器"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def create_subscriber(self, email, name=None, phone=None, plan='free'):
        """创建新订阅用户"""
        cursor = self.conn.cursor()
        
        # 7天试用期
        trial_end = (datetime.now() + timedelta(days=7)).date()
        
        cursor.execute('''
        INSERT INTO subscribers (email, name, phone, plan, trial_end_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, name, phone, plan, trial_end, 'trial'))
        
        self.conn.commit()
        subscriber_id = cursor.lastrowid
        
        print(f"✅ 创建订阅用户: {email}, ID: {subscriber_id}, 试用期至: {trial_end}")
        return subscriber_id
    
    def record_payment(self, subscriber_id, amount, plan, payment_method, proof_path=None):
        """
        记录支付事件
        状态: pending → paid_unconfirmed（用户上传凭证后）
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO payment_events 
        (subscriber_id, amount, plan, payment_method, payment_proof, status, paid_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            subscriber_id, 
            amount, 
            plan, 
            payment_method, 
            proof_path,
            PaymentStatus.PAID_UNCONFIRMED.value,
            datetime.now()
        ))
        
        self.conn.commit()
        payment_id = cursor.lastrowid
        
        print(f"⏳ 记录支付: 用户{subscriber_id}, ¥{amount/100}, 待确认")
        return payment_id
    
    def confirm_payment(self, payment_id, confirmed_by, notes=None):
        """
        人工确认支付（你操作）
        状态: paid_unconfirmed → confirmed → active
        """
        cursor = self.conn.cursor()
        
        # 获取支付信息
        cursor.execute('''
        SELECT subscriber_id, plan, amount FROM payment_events WHERE id = ?
        ''', (payment_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"❌ 支付记录不存在: {payment_id}")
            return False
        
        subscriber_id, plan, amount = row
        
        # 计算到期时间
        if plan == 'standard':
            expires_at = datetime.now() + timedelta(days=30)
        elif plan == 'premium':
            expires_at = datetime.now() + timedelta(days=30)
        else:
            expires_at = datetime.now() + timedelta(days=30)
        
        # 更新支付记录
        cursor.execute('''
        UPDATE payment_events 
        SET status = ?, confirmed_at = ?, confirmed_by = ?, notes = ?, activated_at = ?, expires_at = ?
        WHERE id = ?
        ''', (
            PaymentStatus.ACTIVE.value,
            datetime.now(),
            confirmed_by,
            notes,
            datetime.now(),
            expires_at,
            payment_id
        ))
        
        # 更新用户状态
        cursor.execute('''
        UPDATE subscribers 
        SET plan = ?, status = ?, paid_until = ?, trial_end_date = NULL
        WHERE id = ?
        ''', (plan, 'active', expires_at.date(), subscriber_id))
        
        self.conn.commit()
        
        print(f"✅ 确认支付: 用户{subscriber_id}已开通{plan}版，到期: {expires_at.date()}")
        return True
    
    def check_expirations(self):
        """检查过期订阅（每天自动运行）"""
        cursor = self.conn.cursor()
        today = datetime.now().date()
        
        # 查找今天过期的用户
        cursor.execute('''
        SELECT s.id, s.email, s.plan, p.expires_at
        FROM subscribers s
        JOIN payment_events p ON s.id = p.subscriber_id
        WHERE s.status = 'active'
        AND p.expires_at <= ?
        AND p.status = 'active'
        ''', (today,))
        
        expired = cursor.fetchall()
        
        for row in expired:
            subscriber_id, email, plan, expires_at = row
            
            # 更新状态为过期
            cursor.execute('''
            UPDATE subscribers SET status = ? WHERE id = ?
            ''', ('expired', subscriber_id))
            
            cursor.execute('''
            UPDATE payment_events SET status = ? WHERE subscriber_id = ? AND status = 'active'
            ''', ('expired', subscriber_id))
            
            print(f"⚠️ 订阅过期: {email}, 原套餐: {plan}")
        
        self.conn.commit()
        return len(expired)
    
    def get_pending_confirmations(self):
        """获取待确认的支付列表（你每天查看）"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT 
            p.id as payment_id,
            s.id as subscriber_id,
            s.email,
            s.name,
            p.amount,
            p.plan,
            p.payment_method,
            p.payment_proof,
            p.paid_at
        FROM payment_events p
        JOIN subscribers s ON p.subscriber_id = s.id
        WHERE p.status = 'paid_unconfirmed'
        ORDER BY p.paid_at ASC
        ''')
        
        rows = cursor.fetchall()
        
        if not rows:
            print("✅ 没有待确认的支付")
            return []
        
        print(f"\n⏳ 待确认支付: {len(rows)} 笔")
        print("-" * 80)
        
        for row in rows:
            print(f"ID: {row['payment_id']}, 用户: {row['email']}, ¥{row['amount']/100}, {row['plan']}, 付款时间: {row['paid_at']}")
        
        return rows
    
    def get_stats(self):
        """获取统计信息"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # 用户统计
        cursor.execute("SELECT COUNT(*) FROM subscribers WHERE status = 'active'")
        stats['active_subscribers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subscribers WHERE status = 'trial'")
        stats['trial_users'] = cursor.fetchone()[0]
        
        # 支付统计
        cursor.execute("SELECT COUNT(*), SUM(amount) FROM payment_events WHERE status = 'active'")
        row = cursor.fetchone()
        stats['paid_subscriptions'] = row[0]
        stats['total_revenue'] = row[1] or 0
        
        cursor.execute("SELECT COUNT(*) FROM payment_events WHERE status = 'paid_unconfirmed'")
        stats['pending_confirmations'] = cursor.fetchone()[0]
        
        return stats

def main():
    """演示用法"""
    manager = SubscriptionManager()
    
    print("=" * 60)
    print("🎯 半自动订阅管理系统")
    print("=" * 60)
    
    # 显示统计
    stats = manager.get_stats()
    print(f"\n📊 当前状态:")
    print(f"   付费用户: {stats['active_subscribers']}")
    print(f"   试用用户: {stats['trial_users']}")
    print(f"   总收入: ¥{stats['total_revenue']/100}")
    print(f"   待确认: {stats['pending_confirmations']}")
    
    # 显示待确认列表
    manager.get_pending_confirmations()
    
    print("\n" + "=" * 60)
    print("💡 用法示例:")
    print("   # 确认支付（你操作）")
    print("   manager.confirm_payment(payment_id=1, confirmed_by='你')")
    print("=" * 60)

if __name__ == "__main__":
    main()
