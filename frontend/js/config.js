const API_BASE_URL = 'http://localhost:5000'; 
// js/config.js - 全局配置
window.AppConfig = {
    API_BASE_URL: 'http://localhost:5000',
    // 或者如果你的后端使用 /api 前缀
    // API_BASE_URL: 'http://localhost:5000/api',
    
    // 或者如果你的后端在不同端口
    // API_BASE_URL: 'http://localhost:3000',
    
    // 模拟数据模式（当后端不可用时启用）
    MOCK_MODE: false,
    
    // API 端点
    API_ENDPOINTS: {
        PATIENTS: '/patients',
        DOCTORS: '/doctors',
        APPOINTMENTS: '/appointments',
        BILLING: '/billing',
        LOGIN: '/login'
    }
};