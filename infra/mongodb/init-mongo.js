db = db.getSiblingDB('fango_logs');
db.createCollection("app_logs");
db.app_logs.createIndex({ "timestamp": 1 });
db.app_logs.createIndex({ "level": 1 });
db.app_logs.createIndex({ "module": 1 });
db.app_logs.createIndex({ "user_id": 1 });

