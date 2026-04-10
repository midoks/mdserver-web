(function () {
  const rangeButtons = document.querySelectorAll('[data-range]');
  let currentRange = '24h';
  let currentStatus = {
    monitorOpen: true,
    onlyNet: true,
  };

  function setActiveRange(range) {
    currentRange = range;
    rangeButtons.forEach((btn) => {
      btn.classList.toggle('is-active', btn.dataset.range === range);
    });
    loadOverview();
  }

  rangeButtons.forEach((btn) => {
    btn.addEventListener('click', () => setActiveRange(btn.dataset.range));
  });

  async function requestJson(url, options) {
    const response = await fetch(url, {
      cache: 'no-store',
      ...options,
    });
    if (!response.ok) {
      throw new Error('request failed');
    }
    return response.json();
  }

  function toPercent(value) {
    if (value === null || value === undefined) return '--';
    return `${Number(value).toFixed(1)}%`;
  }

  function toMbpsFromKB(value) {
    if (value === null || value === undefined) return '--';
    const mbps = (Number(value) * 8) / 1024;
    return `${mbps.toFixed(2)} Mbps`;
  }

  function toMBFromBytes(value) {
    if (value === null || value === undefined) return '--';
    return `${(Number(value) / (1024 * 1024)).toFixed(2)} MB`;
  }

  function updateKpi(summary) {
    if (!summary) {
      return;
    }
    const cpuEl = document.querySelector('[data-metric="cpu_latest"]');
    const memEl = document.querySelector('[data-metric="mem_latest"]');
    const netEl = document.querySelector('[data-metric="net_latest"]');
    const diskEl = document.querySelector('[data-metric="disk_latest"]');

    if (cpuEl) {
      cpuEl.textContent = toPercent(summary.cpu.latest);
      cpuEl.closest('[data-kpi="cpu"]').querySelector('.mw-observe-kpi-desc').textContent = `峰值 ${toPercent(summary.cpu.peak)}`;
      updateMeter(cpuEl.closest('[data-kpi="cpu"]'), summary.cpu.latest, 100);
    }

    if (memEl) {
      memEl.textContent = toPercent(summary.mem.latest);
      memEl.closest('[data-kpi="mem"]').querySelector('.mw-observe-kpi-desc').textContent = `峰值 ${toPercent(summary.mem.peak)}`;
      updateMeter(memEl.closest('[data-kpi="mem"]'), summary.mem.latest, 100);
    }

    if (netEl) {
      netEl.textContent = toMbpsFromKB(summary.net.latest);
      netEl.closest('[data-kpi="net"]').querySelector('.mw-observe-kpi-desc').textContent = `峰值 ${toMbpsFromKB(summary.net.peak)}`;
      updateMeter(netEl.closest('[data-kpi="net"]'), summary.net.latest, summary.net.peak || 1);
    }

    if (diskEl) {
      diskEl.textContent = toMBFromBytes(summary.disk.latest);
      diskEl.closest('[data-kpi="disk"]').querySelector('.mw-observe-kpi-desc').textContent = `峰值 ${toMBFromBytes(summary.disk.peak)}`;
      updateMeter(diskEl.closest('[data-kpi="disk"]'), summary.disk.latest, summary.disk.peak || 1);
    }
  }

  function updateMeter(root, value, max) {
    const meter = root.querySelector('.mw-observe-kpi-meter span');
    if (!meter) return;
    if (value === null || value === undefined || max === null || max === undefined || Number(max) <= 0) {
      meter.style.width = '0%';
      return;
    }
    const pct = Math.min((Number(value) / Number(max)) * 100, 100);
    meter.style.width = `${pct.toFixed(1)}%`;
  }

  function updateEvents(events) {
    const list = document.getElementById('observeEvents');
    if (!list) return;
    list.innerHTML = '';
    if (!events || events.length === 0) {
      const item = document.createElement('li');
      const message = currentStatus.monitorOpen ? '监控正在采样，暂未生成峰值' : '监控未开启，暂无峰值记录';
      item.innerHTML = `<span class="mw-observe-event-dot"></span><div><div class="mw-observe-event-title">暂无可用事件</div><div class="mw-observe-event-time">${message}</div></div>`;
      list.appendChild(item);
      return;
    }
    events.forEach((event) => {
      const item = document.createElement('li');
      item.innerHTML = `<span class="mw-observe-event-dot"></span><div><div class="mw-observe-event-title">${event.title}</div><div class="mw-observe-event-time">${event.time}</div></div>`;
      list.appendChild(item);
    });
  }

  function initChart(domId) {
    const el = document.getElementById(domId);
    if (!el || !window.echarts) return null;
    return window.echarts.init(el);
  }

  const charts = {
    load: initChart('getloadview'),
    cpu: initChart('cupview'),
    mem: initChart('memview'),
    disk: initChart('diskview'),
    net: initChart('network'),
  };

  function buildLineOption(labels, series, yLabel) {
    return {
      animation: false,
      tooltip: { trigger: 'axis' },
      legend: {
        top: 8,
      },
      toolbox: {
        right: 8,
        feature: {
          dataZoom: { yAxisIndex: 'none' },
          restore: {},
          saveAsImage: {},
        },
      },
      grid: { left: '3%', right: '4%', bottom: 44, containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: labels },
      yAxis: { type: 'value', name: yLabel || '' },
      dataZoom: [
        { type: 'inside', start: 0, end: 100 },
        { type: 'slider', bottom: 6, start: 0, end: 100, height: 18 },
      ],
      series,
    };
  }

  function buildEmptyOption(message) {
    return {
      title: {
        text: message || '暂无数据',
        left: 'center',
        top: 'middle',
        textStyle: { color: '#9aa0a6', fontSize: 14, fontWeight: 400 },
      },
      xAxis: { show: false },
      yAxis: { show: false },
      series: [],
    };
  }

  function renderChart(chart, option, hasData, message) {
    if (!chart) return;
    if (!hasData) {
      chart.setOption(buildEmptyOption(message || '暂无监控数据'));
      return;
    }
    chart.setOption(option);
  }

  function getEmptyMessage() {
    if (!currentStatus.monitorOpen) {
      return '监控未开启，请在左侧开启';
    }
    return '监控正在采样，请稍候';
  }

  function renderCharts(series) {
    series = series || {};
    const loadSeries = series.load || { labels: [], one: [], five: [], fifteen: [] };
    const cpuSeries = series.cpu || { labels: [], cpu: [], mem: [] };
    const diskSeries = series.disk || { labels: [], read: [], write: [] };
    const netSeries = series.net || { labels: [], up: [], down: [] };

    const emptyMessage = getEmptyMessage();
    renderChart(charts.load, buildLineOption(loadSeries.labels, [
      { name: '1分钟', type: 'line', data: loadSeries.one, smooth: true },
      { name: '5分钟', type: 'line', data: loadSeries.five, smooth: true },
      { name: '15分钟', type: 'line', data: loadSeries.fifteen, smooth: true },
    ]), loadSeries.labels && loadSeries.labels.length > 0, emptyMessage);

    renderChart(charts.cpu, buildLineOption(cpuSeries.labels, [
      { name: 'CPU使用率', type: 'line', data: cpuSeries.cpu, smooth: true },
    ], '%'), cpuSeries.labels && cpuSeries.labels.length > 0, emptyMessage);

    renderChart(charts.mem, buildLineOption(cpuSeries.labels, [
      { name: '内存使用率', type: 'line', data: cpuSeries.mem, smooth: true },
    ], '%'), cpuSeries.labels && cpuSeries.labels.length > 0, emptyMessage);

    renderChart(charts.disk, buildLineOption(diskSeries.labels, [
      { name: '读取', type: 'line', data: diskSeries.read, smooth: true },
      { name: '写入', type: 'line', data: diskSeries.write, smooth: true },
    ], 'MB'), diskSeries.labels && diskSeries.labels.length > 0, emptyMessage);

    renderChart(charts.net, buildLineOption(netSeries.labels, [
      { name: '上行', type: 'line', data: netSeries.up, smooth: true },
      { name: '下行', type: 'line', data: netSeries.down, smooth: true },
    ], 'Mbps'), netSeries.labels && netSeries.labels.length > 0, emptyMessage);
  }

  async function loadOverview() {
    try {
      const result = await requestJson(`/monitor/api/overview?range=${currentRange}`);
      if (!result.status || !result.data) {
        renderCharts();
        return;
      }
      updateKpi(result.data.summary || {});
      updateEvents(result.data.events || []);
      renderCharts(result.data.series || {});
    } catch (error) {
      renderCharts();
    }
  }

  function resizeCharts() {
    Object.values(charts).forEach((chart) => {
      if (chart) {
        chart.resize();
      }
    });
  }

  async function getStatus() {
    try {
      const form = new URLSearchParams();
      form.append('type', '-1');
      const result = await requestJson('/system/set_control', { method: 'POST', body: form });
      currentStatus.monitorOpen = result.status;
      currentStatus.onlyNet = result.stat_all_status;
      document.getElementById('save_day').value = result.day;
      renderSwitches();
    } catch (error) {
      // ignore
    }
  }

  function renderSwitches() {
    const openContainer = document.getElementById('openJK');
    const netContainer = document.getElementById('statAll');
    if (openContainer) {
      openContainer.innerHTML = `
        <input class="btswitch btswitch-ios" id="monitorSwitch" type="checkbox" ${currentStatus.monitorOpen ? 'checked' : ''}>
        <label class="btswitch-btn" for="monitorSwitch"></label>
      `;
      openContainer.querySelector('input').addEventListener('change', (event) => {
        setControl('openjk', event.target.checked);
      });
    }
    if (netContainer) {
      netContainer.innerHTML = `
        <input class="btswitch btswitch-ios" id="netSwitch" type="checkbox" ${currentStatus.onlyNet ? 'checked' : ''}>
        <label class="btswitch-btn" for="netSwitch"></label>
      `;
      netContainer.querySelector('input').addEventListener('change', (event) => {
        setControl('stat', event.target.checked);
      });
    }
  }

  window.setControl = async function (act, value) {
    let type = '';
    let day = document.getElementById('save_day').value;

    if (act === 'openjk') {
      type = value ? '1' : '0';
      if (Number(day) < 1) {
        layer.msg('保存天数不合法!', { icon: 2 });
        return;
      }
    } else if (act === 'stat') {
      type = value ? '3' : '2';
    } else if (act === 'save_day') {
      type = currentStatus.monitorOpen ? '1' : '0';
      if (Number(day) < 1) {
        layer.msg('保存天数不合法!', { icon: 2 });
        return;
      }
    }

    const form = new URLSearchParams();
    form.append('type', type);
    form.append('day', day);

    try {
      const result = await requestJson('/system/set_control', { method: 'POST', body: form });
      layer.msg(result.msg, { icon: result.status ? 1 : 2 });
      getStatus();
    } catch (error) {
      layer.msg('操作失败', { icon: 2 });
    }
  };

  window.closeControl = async function () {
    layer.confirm('您真的清空所有监控记录吗？', { title: '清空记录', icon: 3, closeBtn: 1 }, async function () {
      const form = new URLSearchParams();
      form.append('type', 'del');
      try {
        const result = await requestJson('/system/set_control', { method: 'POST', body: form });
        layer.msg(result.msg, { icon: result.status ? 1 : 2 });
        loadOverview();
      } catch (error) {
        layer.msg('操作失败', { icon: 2 });
      }
    });
  };

  getStatus();
  loadOverview();
  window.addEventListener('resize', resizeCharts);
  setInterval(() => {
    getStatus();
    loadOverview();
    resizeCharts();
  }, 5000);
})();
