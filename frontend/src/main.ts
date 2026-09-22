import { createApp } from 'vue'
import App from './App.vue'
import { setupVigil } from './vigil'

const app = createApp(App)

await setupVigil(app)

app.mount('#app')
