<template>
  <!-- 全屏模式（考试页面） -->
  <div v-if="isFullscreen" class="fullscreen-container">
    <router-view />
  </div>
  
  <!-- 正常布局 -->
  <el-container v-else class="student-layout">
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-left">
        <div class="logo" @click="router.push('/home')">
          <img src="/favicon.svg" alt="logo" class="logo-img" />
          <span class="logo-text">楚然智考</span>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          router
        >
          <el-menu-item index="/home">
            <el-icon><HomeFilled /></el-icon>
            首页
          </el-menu-item>
          <el-menu-item index="/exam-center">
            <el-icon><Tickets /></el-icon>
            考试中心
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><Clock /></el-icon>
            考试记录
          </el-menu-item>
          <el-menu-item index="/wrong-questions">
            <el-icon><Warning /></el-icon>
            错题本
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><DataLine /></el-icon>
            学习统计
          </el-menu-item>
        </el-menu>
      </div>
      
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="32" :src="userStore.userInfo?.avatar">
              {{ userStore.userInfo?.username?.charAt(0)?.toUpperCase() }}
            </el-avatar>
            <span class="username">{{ userStore.userInfo?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="admin" v-if="userStore.isAdmin">
                <el-icon><Setting /></el-icon>
                管理后台
              </el-dropdown-item>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <!-- 内容区 -->
    <el-main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
    
    <!-- 底部 -->
    <el-footer class="footer">
      <p>© 2024 楚然智考系统 - 让学习更高效</p>
    </el-footer>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 是否全屏模式
const isFullscreen = computed(() => route.meta.fullscreen === true)

const activeMenu = computed(() => {
  const path = route.path
  // 处理子路由高亮
  if (path.startsWith('/exam/') || path.startsWith('/exam-result/')) {
    return '/exam-center'
  }
  return path
})

const handleCommand = (command) => {
  switch (command) {
    case 'admin':
      router.push('/admin/dashboard')
      break
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      userStore.logout()
      break
  }
}
</script>

<style lang="scss" scoped>
.fullscreen-container {
  width: 100vw;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
}

.student-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  
  .header {
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    position: sticky;
    top: 0;
    z-index: 100;
    
    .header-left {
      display: flex;
      align-items: center;
      
      .logo {
        display: flex;
        align-items: center;
        cursor: pointer;
        margin-right: 40px;
        
        .logo-img {
          width: 36px;
          height: 36px;
        }
        
        .logo-text {
          font-size: 20px;
          font-weight: 600;
          color: var(--primary-color);
          margin-left: 10px;
        }
      }
      
      .el-menu {
        border-bottom: none;
        
        .el-menu-item {
          font-size: 15px;
        }
      }
    }
    
    .header-right {
      .user-info {
        display: flex;
        align-items: center;
        cursor: pointer;
        
        .username {
          margin: 0 8px;
          font-size: 14px;
        }
      }
    }
  }
  
  .main-content {
    flex: 1;
    background: var(--bg-color);
    padding: 20px 40px;
  }
  
  .footer {
    background: #fff;
    text-align: center;
    color: var(--text-secondary);
    font-size: 13px;
    border-top: 1px solid var(--border-color);
  }
}

// 响应式
@media (max-width: 768px) {
  .student-layout {
    .header {
      padding: 0 15px;
      
      .header-left {
        .logo {
          margin-right: 10px;
          
          .logo-text {
            display: none;
          }
        }
        
        .el-menu-item {
          padding: 0 10px;
          
          span {
            display: none;
          }
        }
      }
      
      .header-right {
        .username {
          display: none;
        }
      }
    }
    
    .main-content {
      padding: 15px;
    }
  }
}
</style>
