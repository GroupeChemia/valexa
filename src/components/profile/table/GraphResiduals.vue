<template>
  <v-row>
    <v-col>
      <VuePlotly
          :data="residualsData.data"
          :layout="residualsData.layout"
          :display-mode-bar="false"
      />
    </v-col>
    <v-col>
      <VuePlotly
          :data="residualsStudentData.data"
          :layout="residualsStudentData.layout"
          :display-mode-bar="false"
      />
    </v-col>
  </v-row>
</template>

<script>
  import VuePlotly from '@statnett/vue-plotly'

  export default {
    name: "GraphResiduals",
    components: {
      VuePlotly
    },
    props: {
      residualsData: Object,
      residualsStudentData: Object
    }
  }
</script>

<style scoped>

</style>