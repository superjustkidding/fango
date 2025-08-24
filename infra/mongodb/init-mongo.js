db = db.getSiblingDB('fango_logs');

// 创建 capped collection（可选，根据日志量调整）
db.createCollection("app_logs", {
    capped: true,
    size: 100000000,  // 100MB
    max: 1000000      // 最多100万条文档
});

// 创建索引以支持查询和导出效率
db.app_logs.createIndex({ "timestamp": 1 }, { background: true });
db.app_logs.createIndex({ "level": 1 }, { background: true });
db.app_logs.createIndex({ "module": 1 }, { background: true });
db.app_logs.createIndex({ "user_id": 1 }, { background: true });

// 插入一些测试数据
db.app_logs.insertMany([
    {
        timestamp: new Date(),
        level: "INFO",
        module: "auth",
        user_id: "user001",
        message: "用户登录成功"
    },
    {
        timestamp: new Date(),
        level: "ERROR",
        module: "payment",
        user_id: "user002",
        message: "支付失败"
    },
    {
        timestamp: new Date(),
        level: "WARN",
        module: "order",
        user_id: "user003",
        message: "订单超时"
    }
]);

