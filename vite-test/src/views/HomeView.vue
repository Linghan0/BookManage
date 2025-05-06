<template>
  <div class="home-view">
    <!-- 欢迎区 -->
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎使用个人书架</h1>
      <p class="welcome-subtitle">高效管理您的图书资源，体验便捷的书籍记录服务</p>
    </div>

    <!-- 功能卡片区 -->
    <div class="feature-cards">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="feature-card">
            <div class="card-icon">
              <el-icon size="40"><el-icon-collection /></el-icon>
            </div>
            <h3>个人图书管理</h3>
            <p>全面管理图书收藏，支持多种检索方式</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card">
            <div class="card-icon">
              <el-icon size="40"><el-icon-user /></el-icon>
            </div>
            <h3>用户中心</h3>
            <p>[管理员]完善的用户管理，[暂未支持]支持权限分级</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="feature-card">
            <div class="card-icon">
              <el-icon size="40"><el-icon-data-analysis /></el-icon>
            </div>
            <h3>数据统计</h3>
            <p>[未实现]可视化数据分析，助力决策制定</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <!-- 随机一言 -->
    <div class="hitokoto-section">
      <p id="hitokoto">
        <a href="#" id="hitokoto_text">:D 获取中...</a>
        <span id="hitokoto_from" class="hitokoto-meta"></span>
      </p>
    </div>
    <!-- 快速导航区 -->
    <div class="quick-actions">
      <h2 class="section-title">快速开始</h2>
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="$router.push('/books')">
          浏览图书
        </el-button>
        <el-button type="success" size="large" @click="$router.push('/login')">
          用户登录
        </el-button>
        <el-button type="info" size="large" @click="$router.push('/userbooks')">
          管理书架
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

async function fetchHitokoto() {
  try {
    const response = await fetch('https://v1.hitokoto.cn')
    const { uuid, hitokoto: hitokotoText, from, from_who } = await response.json()
    const hitokotoLink = document.getElementById('hitokoto_text') as HTMLAnchorElement
    const hitokotoFrom = document.getElementById('hitokoto_from')
    
    if (hitokotoLink) {
      const type = 'd'  // d:文学
      hitokotoLink.href = `https://hitokoto.cn/?c=${type}&uuid=${uuid}`
      hitokotoLink.textContent = hitokotoText
    }
    
    if (hitokotoFrom) {
      const fromText = from_who ? `${from_who}《${from}》` : `《${from}》`
      hitokotoFrom.textContent = `—— ${fromText}`
    }
  } catch (error) {
    console.error('获取一言失败:', error)
  }
}

onMounted(() => {
  fetchHitokoto()
})
</script>

<style scoped>
.home-view {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  min-height: 100vh;
}

.home-view > * {
  position: relative;
  z-index: 1;
}

.home-view > * {
  position: relative;
  z-index: 1;
}

.hitokoto-section {
  display: block;
  width: fit-content;
  margin: 20px auto;
  font-style: italic;
  color: #606266;
  text-align: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 12px 20px;
}

.hitokoto-meta {
  display: block;
  margin-top: 8px;
  font-size: 22px;
  color: #af1aa8;
  text-align: right;
}

#hitokoto_text {
  font-size: 36px;
  color: #409eff;
  text-decoration: none;
  transition: color 0.3s;
}

#hitokoto_text:hover {
  color: #66b1ff;
}

.welcome-section {
  display: block;
  width: fit-content;
  margin: 0 auto 40px;
  text-align: center;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px 24px;
}

.welcome-title {
  font-size: 36px;
  color: #303133;
  margin-bottom: 16px;
}

.welcome-subtitle {
  font-size: 16px;
  color: #3aa0b3;
}

.feature-cards {
  margin: 40px 0;
}

.feature-card {
  text-align: center;
  height: 100%;
  transition: transform 0.3s;
  background: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.card-icon {
  margin: 20px 0;
  color: #409eff;
}

.quick-actions {
  display: block;
  width: fit-content;
  margin: 60px auto 0;
  text-align: center;
  background: rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 16px 24px;
}

.section-title {
  font-size: 24px;
  color: #303133;
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.action-buttons .el-button {
  min-width: 150px;
}
</style>
