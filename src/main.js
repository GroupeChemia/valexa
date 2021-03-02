import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import store from './store'
import VueI18n from 'vue-i18n'
import VueExcelEditor from 'vue-excel-editor'

import VueProgress from 'vue-progress-path'
import i18n from './i18n'
import router from './router'

Vue.use(VueExcelEditor)
Vue.use(VueProgress)
Vue.use(VueI18n)
Vue.config.productionTip = false

new Vue({
  vuetify,
  store,
  i18n,
  router,
  render: h => h(App)
}).$mount('#app')
