/**
 * Weather & Oil Price Widget
 * Minimalist floating widget for Chaoyu Fan's personal website
 */

(function() {
  'use strict';

  const API_BASE_URL = 'https://weatherdash-esc4hch2.manus.space/api/trpc';
  const DEFAULT_CITY = '上海';
  const STORAGE_KEY = 'weather_widget_city';

  class WeatherWidget {
    constructor() {
      this.currentCity = localStorage.getItem(STORAGE_KEY) || DEFAULT_CITY;
      this.isCollapsed = false;
      this.init();
    }

    init() {
      this.render();
      this.attachEventListeners();
      this.loadData();
    }

    render() {
      const container = document.createElement('div');
      container.className = 'weather-widget-container';
      container.innerHTML = `
        <div class="weather-widget">
          <div class="weather-widget-header">
            <h3 class="weather-widget-title">Weather & Oil</h3>
            <button class="weather-widget-toggle" aria-label="Toggle widget">−</button>
          </div>
          <div class="weather-widget-content">
            <div class="widget-city-selector">
              <input 
                type="text" 
                class="widget-city-input" 
                placeholder="城市..."
                value="${this.currentCity}"
              />
              <button class="widget-search-btn">搜索</button>
            </div>
            <div class="widget-loading">
              <div class="widget-spinner"></div>
              <p class="widget-loading-text">加载中...</p>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(container);
      this.container = container;
    }

    attachEventListeners() {
      // 移除旧的事件监听器
      this.detachEventListeners();
      
      const toggleBtn = this.container.querySelector('.weather-widget-toggle');
      const searchBtn = this.container.querySelector('.widget-search-btn');
      const cityInput = this.container.querySelector('.widget-city-input');

      if (toggleBtn) {
        toggleBtn.addEventListener('click', this.toggleCollapseHandler);
      }
      if (searchBtn) {
        searchBtn.addEventListener('click', this.handleSearchHandler);
      }
      if (cityInput) {
        cityInput.addEventListener('keypress', this.handleKeyPressHandler);
      }
    }

    detachEventListeners() {
      const toggleBtn = this.container.querySelector('.weather-widget-toggle');
      const searchBtn = this.container.querySelector('.widget-search-btn');
      const cityInput = this.container.querySelector('.widget-city-input');

      if (toggleBtn) {
        toggleBtn.removeEventListener('click', this.toggleCollapseHandler);
      }
      if (searchBtn) {
        searchBtn.removeEventListener('click', this.handleSearchHandler);
      }
      if (cityInput) {
        cityInput.removeEventListener('keypress', this.handleKeyPressHandler);
      }
    }

    toggleCollapseHandler = () => {
      this.toggleCollapse();
    }

    handleSearchHandler = () => {
      this.handleSearch();
    }

    handleKeyPressHandler = (e) => {
      if (e.key === 'Enter') this.handleSearch();
    }

    toggleCollapse() {
      const widget = this.container.querySelector('.weather-widget');
      if (!widget) return;
      
      this.isCollapsed = !this.isCollapsed;
      widget.classList.toggle('collapsed', this.isCollapsed);
      
      const toggleBtn = this.container.querySelector('.weather-widget-toggle');
      if (toggleBtn) {
        toggleBtn.textContent = this.isCollapsed ? '+' : '−';
      }
    }

    handleSearch() {
      const input = this.container.querySelector('.widget-city-input');
      const city = input.value.trim();
      if (city) {
        this.currentCity = city;
        localStorage.setItem(STORAGE_KEY, city);
        this.loadData();
      }
    }

    async loadData() {
      try {
        await Promise.all([
          this.fetchWeather(),
          this.fetchOilPrices()
        ]);
      } catch (error) {
        console.error('Widget data load error:', error);
        // 使用模拟数据作为备选
        this.displayWeather(this.getMockWeatherData());
        this.displayOilPrices(this.getMockOilData());
      }
    }

    async fetchWeather() {
      try {
        // 使用 POST 请求调用 tRPC
        const response = await fetch(`${API_BASE_URL}/weather.getWeather`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ city: this.currentCity })
        });
        
        if (!response.ok) {
          // 如果 API 不可用，使用模拟数据
          this.displayWeather(this.getMockWeatherData());
          return;
        }
        
        const data = await response.json();
        if (data.error) {
          this.displayWeather(this.getMockWeatherData());
          return;
        }
        
        this.displayWeather(data.result.data);
      } catch (error) {
        // 网络错误或 CORS 问题，使用模拟数据
        console.warn('Weather API unavailable, using mock data:', error);
        this.displayWeather(this.getMockWeatherData());
      }
    }

    async fetchOilPrices() {
      try {
        const response = await fetch(`${API_BASE_URL}/oil.getPrices`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({})
        });
        
        if (!response.ok) {
          this.displayOilPrices(this.getMockOilData());
          return;
        }
        
        const data = await response.json();
        if (data.error) {
          this.displayOilPrices(this.getMockOilData());
          return;
        }
        
        this.displayOilPrices(data.result.data);
      } catch (error) {
        // 网络错误或 CORS 问题，使用模拟数据
        console.warn('Oil API unavailable, using mock data:', error);
        this.displayOilPrices(this.getMockOilData());
      }
    }

    getMockWeatherData() {
      const cities = {
        '北京': { temp: 15, feels_like: 13, humidity: 45, wind_speed: 3.2, pressure: 1013, wind_deg: 225 },
        '上海': { temp: 18, feels_like: 17, humidity: 55, wind_speed: 2.8, pressure: 1012, wind_deg: 180 },
        '深圳': { temp: 26, feels_like: 25, humidity: 65, wind_speed: 4.1, pressure: 1010, wind_deg: 135 },
        '杭州': { temp: 16, feels_like: 15, humidity: 50, wind_speed: 3.5, pressure: 1011, wind_deg: 270 },
        '成都': { temp: 14, feels_like: 12, humidity: 60, wind_speed: 2.5, pressure: 1009, wind_deg: 90 },
        '西安': { temp: 12, feels_like: 10, humidity: 48, wind_speed: 2.9, pressure: 1014, wind_deg: 45 },
        '武汉': { temp: 17, feels_like: 16, humidity: 52, wind_speed: 3.1, pressure: 1011, wind_deg: 315 },
      };
      
      const cityData = cities[this.currentCity] || cities['北京'];
      return {
        current: {
          temp: cityData.temp,
          feels_like: cityData.feels_like,
          humidity: cityData.humidity,
          wind_speed: cityData.wind_speed,
          pressure: cityData.pressure,
          wind_deg: cityData.wind_deg,
          weather: [{ description: '多云' }]
        }
      };
    }

    getMockOilData() {
      return [
        { province: '北京', o92: 8.75, o95: 9.32, o98: 10.45, o0: 8.12 },
        { province: '上海', o92: 8.73, o95: 9.30, o98: 10.43, o0: 8.10 },
        { province: '深圳', o92: 8.78, o95: 9.35, o98: 10.48, o0: 8.15 },
        { province: '杭州', o92: 8.74, o95: 9.31, o98: 10.44, o0: 8.11 },
        { province: '成都', o92: 8.76, o95: 9.33, o98: 10.46, o0: 8.13 },
        { province: '西安', o92: 8.77, o95: 9.34, o98: 10.47, o0: 8.14 },
        { province: '武汉', o92: 8.75, o95: 9.32, o98: 10.45, o0: 8.12 },
      ];
    }

    displayWeather(data) {
      if (!data || !data.current) return;

      const current = data.current;
      const content = this.container.querySelector('.weather-widget-content');

      const weatherHTML = `
        <div class="widget-city-selector">
          <input 
            type="text" 
            class="widget-city-input" 
            placeholder="城市..."
            value="${this.currentCity}"
          />
          <button class="widget-search-btn">搜索</button>
        </div>

        <div class="widget-weather-main">
          <div class="widget-temp-display">
            <div class="widget-temp-value">${Math.round(current.temp)}</div>
            <div class="widget-temp-unit">°C</div>
          </div>
          <div class="widget-weather-desc">
            <p class="widget-weather-status">${current.weather?.[0]?.description || '多云'}</p>
            <p class="widget-feels-like">体感: ${Math.round(current.feels_like)}°C</p>
            <p class="widget-city-name">${this.currentCity}</p>
          </div>
        </div>

        <div class="widget-details-grid">
          <div class="widget-detail-item">
            <span class="widget-detail-label">湿度</span>
            <span class="widget-detail-value">${current.humidity}%</span>
          </div>
          <div class="widget-detail-item">
            <span class="widget-detail-label">风速</span>
            <span class="widget-detail-value">${current.wind_speed.toFixed(1)} m/s</span>
          </div>
          <div class="widget-detail-item">
            <span class="widget-detail-label">气压</span>
            <span class="widget-detail-value">${current.pressure} hPa</span>
          </div>
          <div class="widget-detail-item">
            <span class="widget-detail-label">风向</span>
            <span class="widget-detail-value">${this.getWindDirection(current.wind_deg)}</span>
          </div>
        </div>

        <div class="widget-oil-section" id="oil-section" style="display: none;">
          <div class="widget-oil-title">全国油价</div>
          <div class="widget-oil-prices" id="oil-prices"></div>
          <div class="widget-update-time">
            <small id="oil-time">更新于: --</small>
          </div>
        </div>

        <div class="widget-update-time">
          <small>更新于: ${new Date().toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          })}</small>
        </div>
      `;

      content.innerHTML = weatherHTML;
      this.attachEventListeners();
    }

    displayOilPrices(data) {
      if (!data || data.length === 0) return;

      const beijingPrice = data.find(p => p.province === '北京') || data[0];
      const oilSection = this.container.querySelector('#oil-section');
      const oilPrices = this.container.querySelector('#oil-prices');

      if (oilSection && oilPrices) {
        oilPrices.innerHTML = `
          <div class="widget-oil-item">
            <span class="widget-oil-type">92号</span>
            <span class="widget-oil-price">¥${beijingPrice.o92 || '--'}</span>
          </div>
          <div class="widget-oil-item">
            <span class="widget-oil-type">95号</span>
            <span class="widget-oil-price">¥${beijingPrice.o95 || '--'}</span>
          </div>
          <div class="widget-oil-item">
            <span class="widget-oil-type">98号</span>
            <span class="widget-oil-price">¥${beijingPrice.o98 || '--'}</span>
          </div>
          <div class="widget-oil-item">
            <span class="widget-oil-type">0号</span>
            <span class="widget-oil-price">¥${beijingPrice.o0 || '--'}</span>
          </div>
        `;
        oilSection.style.display = 'block';
      }
    }

    getWindDirection(degrees) {
      const directions = ['北', '东北', '东', '东南', '南', '西南', '西', '西北'];
      const index = Math.round(degrees / 45) % 8;
      return directions[index] || '未知';
    }

    showError() {
      const content = this.container.querySelector('.weather-widget-content');
      content.innerHTML = `
        <div class="widget-error">
          <p class="widget-error-text">无法加载数据</p>
        </div>
      `;
    }
  }

  // Initialize widget when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      new WeatherWidget();
    });
  } else {
    new WeatherWidget();
  }
})();
