<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>修改密码</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 表单 -->
    <div style="margin: 20px;"></div>
    <el-form label-width="120px" :model="editForm" :rules="rules" ref="editForm">
      <el-form-item prop="old_password" label="原密码">
        <el-input type="password" v-model="editForm.old_password" auto-complete="off" placeholder="原密码"></el-input>
      </el-form-item>
      <el-form-item prop="new_password" label="新密码">
        <el-input type="password" v-model="editForm.new_password" auto-complete="off" placeholder="新密码"></el-input>
      </el-form-item>
      <el-form-item prop="confirm_password" label="确认密码">
        <el-input type="password" v-model="editForm.confirm_password" auto-complete="off" placeholder="确认密码"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button size="small" type="primary" @click="submitForm('editForm')">保存</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { modifyPwd } from '../../api/userMG'
import md5 from 'js-md5'
export default {
  data() {
    return {
      editForm: {
        id: '',
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      // rules表单验证
      rules: {
        old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
        new_password: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
        confirm_password: [{ required: true, message: '请输入确认密码', trigger: 'blur' }]
      }
    }
  },
  methods: {
    submitForm(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          let param = {
            old_password: md5(this.editForm.old_password),
            new_password: md5(this.editForm.new_password),
            confirm_password: md5(this.editForm.confirm_password)
          };
          modifyPwd(param)
            .then(res => {
              if (res.success) {
                this.$message({
                  type: 'success',
                  message: res.msg
                });
                this.editForm.old_password = '';
                this.editForm.new_password = '';
                this.editForm.confirm_password = '';
              } else {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              }
            })
            .catch(err => {
              this.editFormVisible = false;
              this.loading = false;
              this.$message.error('密码修改失败，请稍后再试！')
            })
        } else {
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
.el-input{
  width: 350px;
}
</style>
