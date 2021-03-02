<template>
  <v-row>
      <v-col>
          <VuePlotly
              :data="graphData.data"
              :layout="graphData.layout"
              :display-mode-bar="false"
          />
      </v-col>
    </v-row>
</template>

<script>
  import VuePlotly from '@statnett/vue-plotly'

  export default {
    name: "GraphProfile",
    props: {
      graphData: Object
    },
    components: {
      VuePlotly
    }
  }
</script>

<style scoped>

</style>