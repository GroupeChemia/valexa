module.exports = {
    "lintOnSave": false,

    "pluginOptions": {
        "electronBuilder": {
            "nodeIntegration": true
        }
    },

    "transpileDependencies": [
        "vuetify"
    ],

    pluginOptions: {
      electronBuilder: {
        nodeIntegration: true,
        externals: ['plotly.js-dist', 'moment.js', '@statnett/vue-plotly']
      },
      i18n: {
        locale: 'en',
        fallbackLocale: 'fr',
        localeDir: 'locales',
        enableInSFC: true
      }
    }
}
