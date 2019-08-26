<template>
  <div id="app">
    <file-upload 
      url="http://127.0.0.1:5000/valexa_app/compute/"
      @file-save="ploterData = []"
      @fileupload-success="updatePloter($event)"
      @fileupload-error="failedUpload">
    </file-upload>
    <profile-ploter v-for="data in ploterData" v-bind:key="data.filename"
      v-bind:ploterData="data.profiles"
      v-bind:filename="data.filename">
    </profile-ploter>
  </div>
</template>

<script>
import FileUpload from './components/FileUpload.vue'
import ProfilePloter from './components/ProfilePloter.vue'

export default {
  name: 'app',
  data() {
    return {
      ploterData: [{
        filename: "",
        profiles: [],
      }],
    }
  },
  components: {
    FileUpload,
    ProfilePloter,
  },
  methods: {
    updatePloter(event){
      if (!event.data) {
          alert("No data");
      } else {
        this.ploterData.push({
          "profiles": event.data.profiles,
          "filename": event.filename
          });
      }
    },
    failedUpload(event) {
      alert(event.data);
    },
  }
}

</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  /* margin-top: 60px; */
}
</style>
