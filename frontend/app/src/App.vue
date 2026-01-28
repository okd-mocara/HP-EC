<template>
   <AppHeader />
  <div>
    <router-view />
  </div>
</template>

<script>
  import AppHeader from "@/components/HeaderComponent/MainPage.vue";
  export default({
    components:{
      AppHeader
    }
  })
</script>