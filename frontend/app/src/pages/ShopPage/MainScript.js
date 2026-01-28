import { ref, computed, onMounted } from "vue";

export function useCoffeeShop() {
  const products = ref([]);
  const cart = ref([]);
  const loading = ref(false);
  const error = ref("");

  const customer = {
    customer_name: "テスト太郎",
    customer_email: "test@example.com",
    customer_phone: "09000000000",
    shipping_address1: "1-2-3",
    shipping_address2: "",
    shipping_city: "渋谷区",
    shipping_prefecture: "東京都",
    shipping_postal_code: "1500000",
  };

  const formatJPY = (n) => Number(n).toLocaleString("ja-JP");

  const total = computed(() =>
    cart.value.reduce((sum, line) => sum + line.product.price_jpy * line.qty, 0)
  );

  const fetchProducts = async () => {
    error.value = "";
    const apiUrl = import.meta.env.VITE_API_BASE_URL;
    try {
      const res = await fetch(apiUrl + "/api/products");
      if (!res.ok) throw new Error(`GET /api/products failed: ${res.status}`);
      products.value = await res.json();
    } catch (e) {
      error.value = String(e);
    }
  };

  const addToCart = (p) => {
    const found = cart.value.find((x) => x.product.id === p.id);
    if (found) found.qty += 1;
    else cart.value.push({ product: p, qty: 1 });
  };

  const checkout = async () => {
    if (cart.value.length === 0) return;

    loading.value = true;
    error.value = "";

    try {
      const body = {
        ...customer,
        items: cart.value.map((l) => ({
          product_id: l.product.id,
          quantity: l.qty,
        })),
      };

      const res = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error(`POST /api/checkout failed: ${res.status}`);

      const data = await res.json();
      window.location.href = data.checkout_url;
    } catch (e) {
      error.value = String(e);
    } finally {
      loading.value = false;
    }
  };

  onMounted(fetchProducts);

  return {
    products,
    cart,
    loading,
    error,
    total,
    formatJPY,
    addToCart,
    checkout,
  };
}
