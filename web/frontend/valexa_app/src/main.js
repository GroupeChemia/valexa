import Vue from 'vue'
import App from './App.vue'
import axios from "axios"
import VeeValidate from "vee-validate"

Vue.config.productionTip = false;

Vue.use(VeeValidate, {
  classes: true
});

axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';


new Vue({
  render: h => h(App),
}).$mount('#app')
