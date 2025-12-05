<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <img src="/favicon.svg" alt="logo" class="logo-img" />
        <span v-show="!isCollapse" class="logo-text">楚然智考</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#fff"
        router
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>控制台</template>
        </el-menu-item>
        
        <el-sub-menu index="user-manage" v-if="hasPermission('user:view')">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/admin/users">用户列表</el-menu-item>
          <el-menu-item index="/admin/roles" v-if="hasPermission('role:view')">角色管理</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="question-manage" v-if="hasPermission('question:view')">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>题库管理</span>
          </template>
          <el-menu-item index="/admin/questions">题目列表</el-menu-item>
          <el-menu-item index="/admin/questions/import" v-if="hasPermission('question:import')">导入题库</el-menu-item>
          <el-menu-item index="/admin/knowledge" v-if="hasPermission('knowledge:view')">知识点管理</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="exam-manage" v-if="hasPermission('exam:view')">
          <template #title>
            <el-icon><Tickets /></el-icon>
            <span>考试管理</span>
          </template>
          <el-menu-item index="/admin/exams">考试列表</el-menu-item>
          <el-menu-item index="/admin/exams/create" v-if="hasPermission('exam:create')">创建考试</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon 
            class="collapse-btn" 
            @click="isCollapse = !isCollapse"
          >
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">
              {{ $route.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
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
                <el-dropdown-item command="student">
                  <el-icon><Monitor /></el-icon>
                  切换到学员端
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
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

const hasPermission = (permission) => {
  return userStore.hasPermission(permission)
}

const handleCommand = (command) => {
  switch (command) {
    case 'student':
      router.push('/home')
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
.admin-layout {
  height: 100vh;
  
  .sidebar {
    background-color: #001529;
    transition: width 0.3s;
    overflow: hidden;
    
    .logo {
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 16px;
      
      .logo-img {
        width: 32px;
        height: 32px;
      }
      
      .logo-text {
        color: #fff;
        font-size: 18px;
        font-weight: 600;
        margin-left: 10px;
        white-space: nowrap;
      }
    }
    
    .el-menu {
      border-right: none;
    }
  }
  
  .main-container {
    flex-direction: column;
    
    .header {
      background: #fff;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
      
      .header-left {
        display: flex;
        align-items: center;
        
        .collapse-btn {
          font-size: 20px;
          cursor: pointer;
          margin-right: 20px;
          
          &:hover {
            color: var(--primary-color);
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
          }
        }
      }
    }
    
    .main-content {
      background: var(--bg-color);
      padding: 20px;
      overflow-y: auto;
    }
  }
}
</style>
