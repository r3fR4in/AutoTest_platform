<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/apiTest/apiManagement' }">接口管理</el-breadcrumb-item>
      <el-breadcrumb-item :to="{
      path: '/apiTest/apiManagement/apiTestCase',
      query: {
          api_id: api_id
        }
      }">测试用例</el-breadcrumb-item>
      <el-breadcrumb-item>工作台</el-breadcrumb-item>
    </el-breadcrumb>
    <div style="margin: 20px;"></div>
    <el-form :model="apiData" label-width="70px" label-position="left" size="small">
      <!-- 请求链接 -->
      <el-form-item label="标题">
        <el-input size="small" v-model="apiData.title" auto-complete="off" placeholder="标题" style="width: 680px"></el-input>
        <el-button size="small" type="primary" style="margin-left: 20px" @click="debug">调试</el-button>
        <el-button size="small" type="primary" style="margin-left: 10px" @click="save">保存</el-button>
      </el-form-item>
      <el-form-item label="url">
        <el-input class="input-with-select" v-model="apiData.url" size="small" style="width: 680px" :disabled="true">
          <el-select v-model="request_method_select" slot="prepend" placeholder="请选择" size="small" style="width: 100px" disabled="true">
            <el-option
              v-for="item in request_method_options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-input>
      </el-form-item>
      <el-form-item label="字符编码">
        <el-input size="small" v-model="apiData.encode" auto-complete="off" placeholder="字符编码" style="width: 680px"></el-input>
      </el-form-item>
      <el-checkbox v-model="apiData.verify">跳过SSL校验</el-checkbox>
      <el-checkbox v-model="apiData.assert">是否需要断言</el-checkbox>
      <el-checkbox v-model="apiData.postProcessor">后置处理</el-checkbox>
      <div style="margin-top: 18px" v-show="apiData.assert">
        <el-form-item label="断言">
          <el-input
            type="textarea"
            :rows="3"
            placeholder='输入预取断言字段，[{"pattern":"in", "content":"success1"},{"pattern":"equal", "content":"success2"},{"pattern":"not in", "content":"success3"},{"pattern":"not equal", "content":"success4"}]'
            v-model="apiData.assert_content"
            style="margin-top: 10px">
          </el-input>
        </el-form-item>
      </div>
      <div style="margin-top: 18px" v-show="apiData.postProcessor">
        <el-form-item label="后置处理">
          <el-input
            type="textarea"
            :rows="3"
            placeholder='输入匹配规则，如{"name1":"key1[0].key2","name2":"key3"}，可获取响应头和响应体的数据存入环境变量，现仅适用于响应体是json格式的情况'
            v-model="apiData.post_processor_content"
            style="margin-top: 10px">
          </el-input>
        </el-form-item>
      </div>
      <el-tabs v-model="activeName" @tab-click="handleClick" type="border-card" style="margin-top: 18px">
        <el-tab-pane label="Headers" name="first">
          <el-input
            type="textarea"
            :rows="6"
            placeholder='输入字典，如：{"Content-Type": "application/json;charset=UTF-8", "Authorization": "xxxxxxxxxxxxx"}'
            v-model="apiData.request_header">
          </el-input>
        </el-tab-pane>
        <el-tab-pane label="Body" name="second" id="body" v-bind:disabled="this.apiData.request_file.length !== 0">
          <el-input
            type="textarea"
            :rows="6"
            placeholder='输入字典，如：{ "channel": "whatsapp", "to": "85259842833", "whatsapp":{ "type":"text", "text": { "body": "测试" }, "preview_url":false } }'
            v-model="apiData.request_body">
          </el-input>
        </el-tab-pane>
        <!--<el-tab-pane label="Params" name="third" id="param" v-bind:disabled="this.apiData.request_body !== '' || this.apiData.request_file.length !== 0">
          <el-input
            type="textarea"
            :rows="6"
            placeholder='输入字典，以params形式传输，如：{ "channel": "whatsapp", "to": "85259842833", "whatsapp":{ "type":"text", "text": { "body": "测试" }, "preview_url":false } }'
            v-model="apiData.request_param">
          </el-input>
        </el-tab-pane>-->
        <el-tab-pane label="Upload" name="fourth" id="upload" v-bind:disabled="this.apiData.request_body !== ''">
          <div style="width: 360px">
            <el-upload
              class="upload-demo"
              action="/apiTest/uploadFile"
              :headers="uploadToken"
              :data="uploadData"
              :with-credentials="true"
              :on-remove="removeFile"
              :on-success="uploadSuccess"
              :before-remove="beforeRemove"
              :file-list="apiData.request_file">
              <el-button size="small" type="primary">点击上传</el-button>
              <div slot="tip" class="el-upload__tip">現在只支持上傳一個文件，多個文件的情況等遇到了再去擴展</div>
            </el-upload>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-form>
    <div style="margin-top: 20px;">
      <el-card class="box-card;">
        <el-scrollbar style="height: 500px;overflow-wrap:break-word;">
          <div v-for="value in debugLog">
            <div v-if="value.includes('INFO')">
              <!--<span v-if="value.includes('{')">{{value.split(' : ')[0]+' : '}}{{jsonView(value)}}</span>-->
              <span v-if="value.includes('{')">{{value.split(' : ')[0]+' : '+value.split(' : ')[1].split(':')[0]+':'}}<JsonView :json="jsonView(value)"></JsonView></span>
              <span v-else>{{value}}</span>
            </div>
            <div v-else-if="value.includes('ERROR')">
              <span style="color: red">{{value}}</span>
            </div>
          </div>
        </el-scrollbar>
      </el-card>
    </div>
  </div>
</template>

<script>
  import {apiTestcaseData, debugApi, saveApiTestcase, deleteUploadFile} from '../../api/apiTestApi'
  import JsonView from '../../components/JsonView'
export default {
  components: {JsonView},
  data() {
    return{
      id: '',
      api_id: '',
      request_method_select: '',
      activeName: 'first',
      // assert_pattern: [{
      //   value: 'in',
      //   label: '包含'
      // },{
      //   value: 'equal',
      //   label: '相等'
      // },{
      //   value: 'not in',
      //   label: '不包含'
      // },{
      //   value: 'not equal',
      //   label: '不相等'
      // }],
      request_method_options: [{
        value: 'GET',
        label: 'GET'
      },{
        value: 'POST',
        label: 'POST'
      },{
        value: 'PUT',
        label: 'PUT'
      },{
        value: 'DELETE',
        label: 'DELETE'
      }],
      apiData: {
        api_id: '',
        encode: '',
        id: '',
        request_body: '',
        // request_param: '',
        request_header: '',
        request_file: [],
        request_method: '',
        title: '',
        url: '',
        verify: true,
        assert: false,
        assert_content: '',
        postProcessor: false,
        post_processor_content: ' '
      },
      debugLog: [],
      uploadData: {id: ''},
      // 獲取緩存中的token
      uploadToken:{'Authorization': localStorage.getItem('logintoken')},
    }
  },
  created() {
    this.getParams();
    this.getData();
  },
  methods: {
    getData(parameter){
      parameter = {
        id: this.id,
        api_id: this.api_id
      };
      apiTestcaseData(parameter)
        .then(res => {
          if (res.success == false) {
            this.$message({
              type: 'info',
              message: res.msg
            })
          } else {
            this.apiData.api_id = res.data.api_id;
            if(res.data.encode === '') {
              this.apiData.encode = 'utf8'
            } else {
              this.apiData.encode = res.data.encode;
            }
            this.apiData.id = res.data.id;
            this.apiData.request_body = res.data.request_body;
            // this.apiData.request_param = res.data.request_param;
            this.apiData.request_header = res.data.request_header;
            this.apiData.request_method = res.data.request_method;
            this.apiData.title = res.data.title;
            this.apiData.url = res.data.url;
            this.apiData.verify = res.data.verify === 'true';
            this.request_method_select = res.data.request_method;
            this.apiData.assert = res.data.is_assert === 'true';
            // this.apiData.assert_pattern = res.data.assert_pattern;
            this.apiData.assert_content = res.data.assert_content;
            this.apiData.postProcessor = res.data.is_post_processor === 'true';
            this.apiData.post_processor_content = res.data.post_processor_content;
            this.apiData.request_file = res.data.file_name;
          }
        })
        .catch(err => {
          this.loading = false;
          console.log(err);
          this.$message.error('数据加载失败，请稍后再试！')
        })
    },
    handleClick(tab, event) {
      // console.log(tab, event);
    },
    getParams(){
      // 取到路由带过来的参数
      this.id = this.$route.query.id;
      this.api_id = this.$route.query.api_id;
      this.uploadData.id = this.$route.query.id;
    },
    save(){
      this.apiData.post_processor_content = ''; // 不知道爲什麽初始化值為undefined，所以在這裏設為空格
      saveApiTestcase(this.apiData)
        .then(res => {
          if (res.success) {
            this.$message({
              type: 'success',
              message: res.msg
            });
            if (res.hasOwnProperty('id')){
              this.id = res.id;
              this.apiData.id = res.id;
              this.uploadData.id = res.id;
            }
          } else {
            this.$message({
              type: 'info',
              message: res.msg
            })
          }
        })
        .catch(err => {
          this.$message.error('保存失败，请稍后再试！')
        })
    },
    sleep(n) {
        var start = new Date().getTime();
        //  console.log('休眠前：' + start);
        while (true) {
            if (new Date().getTime() - start > n) {
                break;
            }
        }
        // console.log('休眠后：' + new Date().getTime());
    },
    //调试
    debug(){
      debugApi(this.apiData)
        .then(res => {
          if (res.success){
            this.debugLog = res.data;
            console.log(this.debugLog);
          } else {
            this.$message({
              type: 'info',
              message: res.msg
            })
          }
        })
    },
    //切换json显示
    jsonView(str){
      let v = str.match(/\{.*\}/);
      try {
        // console.log(v[0]);
        // console.log(typeof jsonData);
        // console.log(jsonData);
        return JSON.parse(v[0]);
      } catch (e) {
        console.log(e);
        return str
      }
    },
    //上传成功的钩子
    uploadSuccess(res, file, fileList){
      if (this.apiData.request_file === ''){
        this.apiData.request_file = [];
      }
      this.apiData.request_file.push({name: res.file_name, realname: res.real_file_name});
      console.log(this.apiData.request_file);
    },
    beforeRemove(file, fileList) {
        return this.$confirm(`确定移除 ${ file.name }？`)
    },
    removeFile(file, fileList){
      let parameter = {
        id: this.apiData.id,
        file: file.name
      };
      deleteUploadFile(parameter)
        .then(res => {
          if (res.success) {
            this.$message({
              type: 'success',
              message: res.msg
            });
            this.apiData.request_file.some((item, i) => {
              if (item.name === file.name) {
                this.apiData.request_file.splice(this.apiData.request_file.indexOf(i), 1);
                return true;
              }
            });
            console.log(this.apiData.request_file);
          } else {
            this.$message({
              type: 'info',
              message: res.msg
            })
          }
        })
        .catch(err => {
          console.log(err);
          this.loading = false;
          this.$message.error('移除文件失败，请稍后再试！')
        })
    }
  }
}
</script>

<style scoped>
.el-select {
    width: 130px;
  }
.input-with-select .el-input-group__prepend {
  background-color: #fff;
}
/deep/ textarea {
 font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif !important;
}
</style>
