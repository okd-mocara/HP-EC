<template>
  <div class="shop-page">
    <h1>Coffee Beans</h1>

    <h2>商品</h2>
    <ul class="product-list">
      <li v-for="p in products" :key="p.id">
        <b>{{ p.name }}</b> — ¥{{ formatJPY(p.price_jpy) }}
        <button class="add-cart-btn" @click="addToCart(p)">
          カートに追加
        </button>
      </li>
    </ul>

    <h2>カート</h2>
    <p v-if="cart.length === 0">空です</p>

    <div v-else>
      <ul>
        <li v-for="line in cart" :key="line.product.id">
          {{ line.product.name }} × {{ line.qty }}
        </li>
      </ul>

      <p>
        合計: <b>¥{{ formatJPY(total) }}</b>
      </p>

      <button :disabled="loading" @click="checkout">
        {{ loading ? "処理中..." : "Stripeで購入する" }}
      </button>

      <p v-if="error" class="error-text">
        Error: {{ error }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { useCoffeeShop } from "./MainScript.js";

const {
  products,
  cart,
  loading,
  error,
  total,
  formatJPY,
  addToCart,
  checkout,
} = useCoffeeShop();
</script>

<style scoped lang="scss">
.shop-page {
  padding: 24px;
  font-family: system-ui;
  max-width: 800px;

  @include sp {
    background: $color-error;
  }
}

.product-list li {
  margin-bottom: 8px;
}

.add-cart-btn {
  margin-left: 8px;
}

.error-text {
  color: crimson;
  margin-top: 12px;
}

</style>