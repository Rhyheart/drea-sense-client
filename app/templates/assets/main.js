const { createApp, ref, onMounted, onUnmounted } = Vue

createApp({
    setup() {
        // 定义客户端状态常量
        const CLIENT_STATUS = {
            DISCONNECTED: '未连接',
            CONNECTED: '已连接'
        }

        // 响应式状态
        const isLoggedIn = ref(false)
        const error = ref('')
        const form = ref({
            username: '',
            password: ''
        })
        const systemInfo = ref({})
        const isLoading = ref(false)
        let statusTimer = null  // 状态更新定时器

        // 格式化时间
        const formatTime = (time) => {
            return time ? new Date(time).toLocaleString() : '未知'
        }

        // 封装请求函数
        const request = async (url, options = {}) => {
            try {
                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                })
                const data = await response.json()
                
                if (data.code === 200) {
                    return { success: true, data: data.data }
                }
                return { success: false, message: data.message }
            } catch (e) {
                console.error('请求失败:', e)
                return { 
                    success: false, 
                    message: '请求失败，请检查网络连接和客户端状态'
                }
            }
        }

        // 修改检查登录状态函数
        const checkLoginStatus = async () => {
            const { success, data } = await request('/api/auth/status')
            if (success) {
                systemInfo.value = data
                isLoggedIn.value = true
            } else {
                isLoggedIn.value = false
                systemInfo.value.client_status = CLIENT_STATUS.ERROR
                localStorage.removeItem('loginData')
            }
        }

        // 修改状态更新定时器
        const startStatusUpdate = () => {
            if (statusTimer) {
                clearInterval(statusTimer)
            }
            statusTimer = setInterval(async () => {
                if (isLoggedIn.value) {
                    const { success, data } = await request('/api/auth/status')
                    if (success) {
                        systemInfo.value = data
                    } else {
                        systemInfo.value.client_status = CLIENT_STATUS.ERROR
                    }
                }
            }, 5000)
        }

        // 停止状态更新
        const stopStatusUpdate = () => {
            if (statusTimer) {
                clearInterval(statusTimer)
                statusTimer = null
            }
        }

        // 修改登录处理
        const handleLogin = async () => {
            if (isLoading.value) return
            
            isLoading.value = true
            error.value = ''
            
            const { success, data, message } = await request('/api/login', {
                method: 'POST',
                body: JSON.stringify(form.value)
            })

            if (success) {
                await checkLoginStatus()
                startStatusUpdate()
            } else {
                error.value = message
            }
            
            isLoading.value = false
        }

        // 修改加载配置函数
        const loadConfig = async () => {
            const { success, data } = await request('/api/config')
            if (success && data) {
                form.value = data
            }
        }

        // 修改退出登录处理
        const handleLogout = async () => {
            if (isLoading.value) return
            
            isLoading.value = true
            const { success } = await request('/api/auth/logout', {
                method: 'POST'
            })
            
            if (success) {
                isLoggedIn.value = false
                systemInfo.value = {}
                error.value = ''
                stopStatusUpdate()
                loadConfig()
            }
            
            isLoading.value = false
        }

        // 添加授权页面状态
        const isAuthPage = ref(false)
        
        // 检查URL参数
        const checkAuthParam = () => {
            const urlParams = new URLSearchParams(window.location.search)
            isAuthPage.value = urlParams.get('auth') === 'true'
            isViewMode.value = urlParams.get('view') === 'true'
        }
        
        // 处理返回按钮点击
        const handleReturn = () => {
            window.close()
        }
        
        // 修改页面加载处理
        onMounted(async () => {
            await checkLoginStatus()
            if (isLoggedIn.value) {
                // 如果已登录，开始定时更新状态
                startStatusUpdate()
            } else {
                loadConfig()
            }
            checkAuthParam()
        })

        // 组件卸载时清理
        onUnmounted(() => {
            stopStatusUpdate()
        })

        // 在 setup 中添加 isViewMode 状态
        const isViewMode = ref(false)

        // 返回模板需要的数据和方法
        return {
            isLoggedIn,
            error,
            form,
            systemInfo,
            handleLogin,
            handleLogout,
            formatTime,
            isLoading,
            CLIENT_STATUS,  // 导出状态常量供模板使用
            isAuthPage,
            isViewMode,  // 添加此行
            handleReturn,
        }
    }
}).mount('#app')