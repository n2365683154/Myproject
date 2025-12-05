/**
 * 楚然智考系统 - 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

// 布局组件
const AdminLayout = () => import('@/layouts/AdminLayout.vue')
const StudentLayout = () => import('@/layouts/StudentLayout.vue')

// 公共页面
const Login = () => import('@/views/Login.vue')
const NotFound = () => import('@/views/NotFound.vue')

// 管理员页面
const Dashboard = () => import('@/views/admin/Dashboard.vue')
const UserList = () => import('@/views/admin/UserList.vue')
const RoleList = () => import('@/views/admin/RoleList.vue')
const QuestionList = () => import('@/views/admin/QuestionList.vue')
const QuestionEdit = () => import('@/views/admin/QuestionEdit.vue')
const QuestionImport = () => import('@/views/admin/QuestionImport.vue')
const KnowledgeTree = () => import('@/views/admin/KnowledgeTree.vue')
const ExamList = () => import('@/views/admin/ExamList.vue')
const ExamEdit = () => import('@/views/admin/ExamEdit.vue')
const ExamStatistics = () => import('@/views/admin/ExamStatistics.vue')

// 学员页面
const StudentHome = () => import('@/views/student/Home.vue')
const ExamCenter = () => import('@/views/student/ExamCenter.vue')
const TakeExam = () => import('@/views/student/TakeExam.vue')
const ExamResult = () => import('@/views/student/ExamResult.vue')
const ExamHistory = () => import('@/views/student/ExamHistory.vue')
const WrongQuestions = () => import('@/views/student/WrongQuestions.vue')
const StudyStatistics = () => import('@/views/student/StudyStatistics.vue')
const Profile = () => import('@/views/student/Profile.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录', public: true }
  },
  
  // 管理员路由
  {
    path: '/admin',
    component: AdminLayout,
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '控制台', icon: 'Odometer' }
      },
      {
        path: 'users',
        name: 'UserList',
        component: UserList,
        meta: { title: '用户管理', icon: 'User', permission: 'user:view' }
      },
      {
        path: 'roles',
        name: 'RoleList',
        component: RoleList,
        meta: { title: '角色管理', icon: 'UserFilled', permission: 'role:view' }
      },
      {
        path: 'questions',
        name: 'QuestionList',
        component: QuestionList,
        meta: { title: '题库管理', icon: 'Document', permission: 'question:view' }
      },
      {
        path: 'questions/create',
        name: 'QuestionCreate',
        component: QuestionEdit,
        meta: { title: '添加题目', permission: 'question:create' }
      },
      {
        path: 'questions/:id/edit',
        name: 'QuestionEdit',
        component: QuestionEdit,
        meta: { title: '编辑题目', permission: 'question:update' }
      },
      {
        path: 'questions/import',
        name: 'QuestionImport',
        component: QuestionImport,
        meta: { title: '导入题库', icon: 'Upload', permission: 'question:import' }
      },
      {
        path: 'knowledge',
        name: 'KnowledgeTree',
        component: KnowledgeTree,
        meta: { title: '知识点管理', icon: 'Collection', permission: 'knowledge:view' }
      },
      {
        path: 'exams',
        name: 'ExamList',
        component: ExamList,
        meta: { title: '考试管理', icon: 'Tickets', permission: 'exam:view' }
      },
      {
        path: 'exams/create',
        name: 'ExamCreate',
        component: ExamEdit,
        meta: { title: '创建考试', permission: 'exam:create' }
      },
      {
        path: 'exams/:id/edit',
        name: 'ExamEdit',
        component: ExamEdit,
        meta: { title: '编辑考试', permission: 'exam:update' }
      },
      {
        path: 'exams/:id/statistics',
        name: 'ExamStatistics',
        component: ExamStatistics,
        meta: { title: '考试统计', permission: 'stats:view' }
      }
    ]
  },
  
  // 学员路由
  {
    path: '/',
    component: StudentLayout,
    redirect: '/home',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'home',
        name: 'StudentHome',
        component: StudentHome,
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: 'exam-center',
        name: 'ExamCenter',
        component: ExamCenter,
        meta: { title: '考试中心', icon: 'Tickets' }
      },
      {
        path: 'exam/:id',
        name: 'TakeExam',
        component: TakeExam,
        meta: { title: '在线考试', fullscreen: true }
      },
      {
        path: 'exam-result/:id',
        name: 'ExamResult',
        component: ExamResult,
        meta: { title: '考试结果' }
      },
      {
        path: 'history',
        name: 'ExamHistory',
        component: ExamHistory,
        meta: { title: '考试记录', icon: 'Clock' }
      },
      {
        path: 'wrong-questions',
        name: 'WrongQuestions',
        component: WrongQuestions,
        meta: { title: '错题本', icon: 'Warning' }
      },
      {
        path: 'statistics',
        name: 'StudyStatistics',
        component: StudyStatistics,
        meta: { title: '学习统计', icon: 'DataLine' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: Profile,
        meta: { title: '个人中心', icon: 'User' }
      }
    ]
  },
  
  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面不存在', public: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '楚然智考系统'} - 楚然智考`
  
  // 公共页面直接放行
  if (to.meta.public) {
    next()
    return
  }
  
  const userStore = useUserStore()
  const token = userStore.token
  
  // 未登录跳转登录页
  if (!token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 获取用户信息
  if (!userStore.userInfo) {
    try {
      await userStore.getUserInfo()
    } catch (error) {
      userStore.logout()
      next({ name: 'Login' })
      return
    }
  }
  
  // 检查角色权限
  if (to.meta.roles && to.meta.roles.length > 0) {
    const hasRole = to.meta.roles.some(role => userStore.roles.includes(role))
    if (!hasRole && !userStore.userInfo?.is_superuser) {
      next({ name: 'StudentHome' })
      return
    }
  }
  
  // 检查具体权限
  if (to.meta.permission) {
    if (!userStore.hasPermission(to.meta.permission)) {
      ElMessage.error('没有访问权限')
      next(from.fullPath || '/')
      return
    }
  }
  
  next()
})

export default router
