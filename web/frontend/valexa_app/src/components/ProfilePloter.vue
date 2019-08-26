<template>
  <div id="plots">
    <div class="profile" v-for="(profile, i) in ploterData" v-bind:key="i">
      <profile-table 
        v-bind:profile="profile"
        v-bind:filename="filename">
      </profile-table>
      <div v-bind:id="plot_suffix+filename+i" class="plot"></div>
      <div v-bind:id="'linearity_'+filename+i" class="plot"></div>
      <img v-bind:id="plot_suffix+filename+i+'_export'">
      <img v-bind:id="'linearity_'+filename+i+'_export'">
    </div>
  </div>
</template>

<script>
import { ProfilePlot, ProfileLinearity } from "../ploting/__target__/canvas.js";
import Plotly from "plotly.js";
import ProfileTable from "./ProfileTable";

export default {
  name: "ProfilePloter",
  props: {
    filename: String,
    ploterData: Array
  },
  components: {
    ProfileTable,
  },
  data() {
    return {
      plot_suffix: "plot_"
    };
  },
  mounted() {
    var i = -1;

    for (const profile of this.ploterData) {
      i += 1;
      let fig_validity = ProfilePlot(profile).figure;
      fig_validity.config = { responsive: true };
      Plotly.react(
        this.plot_suffix + this.filename + i, fig_validity
      );

      let fig_linearity = ProfileLinearity(profile).figure
      fig_linearity.config = { responsive: true };
      Plotly.react(
        "linearity_" + this.filename + i, fig_linearity
      );

      /**Image export code for possible future use */
      // let img_jpg = document.getElementById('export_'+this.filename + i);
      // .then(function(gd) {
      //   Plotly.toImage(
      //     gd, 
      //     {height: gd.offsetHeight, width: gd.offsetWidth}
      //   )
      //   .then(function(url) {
      //         img_jpg.src = url;
      //         gd.innerHTML = "";
      //     })
      // });
    }
  }
};
</script>

<style scoped>
#plots {
  max-width: 1000px;
  margin-left: auto;
  margin-right: auto;
}
.profile {
  margin-top: 5vw;
}
</style>