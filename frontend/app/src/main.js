import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 作成した router をインポート

const app = createApp(App)
app.use(router) // アプリに router を適用
app.mount('#app') // #app にマウント