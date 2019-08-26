<template>
  <div id="file-upload">
      <div class="container">
        <div id="drop" @dragenter="handleDragover" @dragover="handleDragover" @drop="handleDrop">
          <div v-if="!isReady">Drop a spreadsheet here</div>
          <div v-else>Ready</div>
        </div>
        <form @submit.prevent="requestProfiles">
          <div id="file-btn">
            <label for="file">
              <p v-if="!isReady">Or select a file</p>
              <p v-else>{{files[0].name}}</p>
            </label>
            <input
              type="file"
              id="file"
              name="file"
              multiple="multiple"
              ref="file"
              v-validate="'ext:xlsx'"
              @change="save($event)"
            />
          </div>
          <div class="spacer"></div>
          <div id="profile-parameters" class="container">
            <div class="parameter">
              <input
                type="text"
                name="acceptance"
                v-model="acceptance"
                v-validate="'required|numeric'"
              /> Acceptance limit
            </div>
            <div class="parameter">
              <input type="text" name="tolerance" v-model="tolerance" v-validate="'required|numeric'" /> Tolerance limit
            </div>
            <div class="parameter">
              <button type="submit" v-bind:disabled="errors.any() || !isReady">evaluate</button>
            </div>
          </div>
        </form>
      </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "FileUpload",
  props: {
    url: String
  },
  data() {
    return {
      files: [],
      acceptance: 20,
      tolerance: 80
    };
  },
  computed: {
    isReady() {
      return this.files.length > 0;
    }
  },
  methods: {
    handleDrop(e) {
      e.stopPropagation();
      e.preventDefault();
      this.save(e);
    },
    handleDragover(e) {
      e.stopPropagation();
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
    },
    save(e) {
      if (e.dataTransfer) {
        this.$refs.file.files = e.dataTransfer.files;
        this.files = e.dataTransfer.files;
      } else {
        this.files = e.target.files;
      }
      this.$emit("file-save");
    },
    requestProfiles() {
      for (const file of this.files) {
        let formData = new FormData();
        formData.append("file", file);
        formData.append("acceptance", this.acceptance);
        formData.append("tolerance", this.tolerance);

        this.uploadFile(formData);
      }
      this.files = [];
      this.$refs.file.value = "";
    },
    uploadFile: function(formData) {
      var vm = this;
      axios({
        method: "POST",
        url: vm.url,
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data"
        },
        responseType: "json"
      })
        .then(function(response) {
          vm.$emit("fileupload-success", {
            data: response.data,
            filename: formData.get("file").name
          });
        })
        .catch(function(error) {
          vm.$emit("fileupload-error", {
            error: error,
            filename: formData.get("file").name
          });
        })
        .finally(function() {});
    }
  }
};
</script>

<style scoped>
.container {
  display: grid;
  max-width: 1000px;
  margin: auto;
}

.spacer {
  height: 5vh;
  width: 100%;
}

a {
  text-decoration: none;
}

#file-upload {
  text-align: center;
}

#drop {
  border: 2px dashed #bbb;
  -moz-border-radius: 5px;
  -webkit-border-radius: 5px;
  border-radius: 5px;
  padding: 25px;
  text-align: center;
  font: 20pt bold, "Vollkorn";
  color: #bbb;
  grid-row-start: 1;
}

#file-btn {
  grid-row-start: 2;
  grid-column-start: 1;
  width: 60%;
  margin: auto;
}
#file-btn input {
  display: none;
}
#file-btn label {
  margin: auto;
  align-items: center;
  width: 100%;
  height: 5vh;
  background-color: rgb(230, 230, 230);
  border-style: solid;
  border-radius: 5px;
  display: flex;
}
#file-btn label p {
  margin: auto;
}

#profile-parameters {
  display: flexbox;
  margin: 0;
}
.parameter {
  display: inline-flex;
}
.parameter input {
  border: 1px solid;
  border-style: solid;
  border-radius: 5px;
  margin-right: 1vw;
  text-align: center;
  outline: none;
}
.parameter input.invalid {
  border-color: crimson;
}
.parameter button {
  width: 171px;
  margin-top: 1vh;
}
</style>
