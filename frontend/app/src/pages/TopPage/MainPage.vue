<template>

    <div class="image_wrapper">
        <img alt="coffee" src="@/assets/images/top_coffee.png">
    </div>
    <div class="menu_wrapper">
        <div class="menu_link">
            <a href="/contact" lass="menu_link_label">お店について</a>
        </div>
        <div class="menu_link">
            <a href="/contact" lass="menu_link_label">出展情報</a>
        </div>
        <div class="menu_link">
            <a href="/shop" lass="menu_link_label">ショッピング</a>
        </div>

    </div>

</template>

<script setup>
import { useMainScript } from "./MainScript.js";

const {
} = useMainScript();
</script>

<style scoped lang="scss"></style>