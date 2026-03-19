#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to write discount_report.py"""

code = '''
import json
import logging
from typing import List
import pandas as pd
from src.discount_models import SegmentAnalysisResult, OptimalDiscountRecommendation, AnalysisResults
from src.discount_constants import PRICE_BAND_ORDER, DISCOUNT_TIER_ORDER

logger = logging.getLogger(__name__)

class HTMLReportGenerator:
    def generate(self, df, analysis_results, recommendations, output_path, gl_price_discount_df=None, input_file_path=None):
        html = self._build_html(df, analysis_results, recommendations, gl_price_discount_df, input_file_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f'HTMLレポートを生成: {output_path}')
    
    def _build_html(self, df, analysis_results, recommendations, gl_price_discount_df=None, input_file_path=None):
        pfs = sorted(df['pf'].dropna().unique().tolist())
        gls = sorted(df['gl'].dropna().unique().tolist()) if 'gl' in df.columns else []
        paid_col = 'paid-flag' if 'paid-flag' in df.columns else 'paid_flag' if 'paid_flag' in df.columns else None
        paid_flags = sorted(df[paid_col].dropna().unique().astype(str).tolist()) if paid_col else []
        analysis_json = json.dumps([r.to_dict() for r in analysis_results], ensure_ascii=False)
        gl_json = gl_price_discount_df.to_json(orient='records', force_ascii=False) if gl_price_discount_df is not None and len(gl_price_discount_df) > 0 else '[]'
        pf_opts = ''.join([f'<option value="{p}">{p}</option>' for p in pfs])
        gl_opts = ''.join([f'<option value="{g}">{g}</option>' for g in gls])
        pf_flag_opts = ''.join([f'<option value="{p}">{p}</option>' for p in paid_flags])
        input_file = input_file_path or 'N/A'
        return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>分析</title><script src="https://cdn.plot.ly/plotly-latest.min.js"></script><style>body{{font-family:sans-serif;margin:20px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:8px}}th{{background:#4CAF50;color:white}}.filter-box{{background:#e3f2fd;padding:15px;margin:10px 0}}.input-box{{background:#fff3e0;padding:15px;margin:10px 0}}.reload-box{{background:#f3e5f5;padding:15px;margin:10px 0}}.reload-box input[type=text]{{width:400px}}.tab-btn{{padding:10px 20px;cursor:pointer}}.tab-btn.active{{background:#4CAF50;color:white}}.tab-content{{display:none;padding:20px;border:1px solid #ddd}}.tab-content.active{{display:block}}.success{{color:#4CAF50}}.warning{{color:#ff9800}}.low{{color:#f44336}}.profit-positive{{background:#e8f5e9}}.profit-negative{{background:#ffebee}}</style></head><body><h1>割引効果分析レポート</h1><p>件数:{len(df):,} / セグメント:{len(analysis_results)} / PF:{len(pfs)} / GL:{len(gls)}</p><p>入力ファイル: {input_file}</p><div class="reload-box"><h3>📂 別ファイルで再分析</h3><p>ファイルパス: <input type="text" id="newFilePath" value="{input_file}"></p><p>コマンド: <code id="cmdDisplay">python -m src.run_discount_analysis "{input_file}" --gl</code></p><button onclick="updateCommand()">コマンド更新</button></div><div class="filter-box"><label>PF:<select id="pfFilter" multiple><option value="all" selected>すべて</option>{pf_opts}</select></label><label>GL:<select id="glFilter" multiple><option value="all" selected>すべて</option>{gl_opts}</select></label><label>PaidFlag:<select id="paidFlagFilter"><option value="all" selected>すべて</option>{pf_flag_opts}</select></label><button onclick="applyFilters()">適用</button><button onclick="resetFilters()">リセット</button></div><div class="input-box"><label>最低利益率(%):<input type="number" id="minProfit" value="20"></label><label>基準利益率(%):<input type="number" id="baseProfit" value="30"></label><button onclick="recalc()">再計算</button></div><div><button class="tab-btn active" onclick="showTab('segment')">セグメント分析</button><button class="tab-btn" onclick="showTab('rec')">推奨割引率</button><button class="tab-btn" onclick="showTab('gl')">GL×価格帯×割引率</button><button class="tab-btn" onclick="showTab('heatmap')">ヒートマップ</button></div><div id="segment" class="tab-content active"><div id="segmentTable"></div></div><div id="rec" class="tab-content"><div id="recTable"></div></div><div id="gl" class="tab-content"><div id="glTable"></div></div><div id="heatmap" class="tab-content"><div id="heatmapChart" style="height:500px"></div></div><script>const data={analysis_json};const glData={gl_json};const pbOrder={json.dumps(PRICE_BAND_ORDER)};const dtOrder={json.dumps(DISCOUNT_TIER_ORDER)};let fData=[...data];let fGl=[...glData];function showTab(t){{document.querySelectorAll(".tab-content").forEach(e=>e.classList.remove("active"));document.querySelectorAll(".tab-btn").forEach(e=>e.classList.remove("active"));document.getElementById(t).classList.add("active");event.target.classList.add("active")}}function getVals(id){{const s=document.getElementById(id);const v=Array.from(s.selectedOptions).map(o=>o.value);return v.includes("all")?null:v}}function applyFilters(){{const pf=getVals("pfFilter");const gl=getVals("glFilter");fData=data.filter(r=>{{if(pf&&r.pf&&!pf.includes(r.pf))return false;if(gl&&r.gl&&!gl.includes(r.gl))return false;return true}});fGl=glData.filter(r=>{{if(gl&&!gl.includes(r.gl))return false;return true}});renderAll()}}function resetFilters(){{document.getElementById("pfFilter").value="all";document.getElementById("glFilter").value="all";document.getElementById("paidFlagFilter").value="all";fData=[...data];fGl=[...glData];renderAll()}}function renderAll(){{renderSeg();recalc();renderGl();renderHeatmap()}}function renderSeg(){{const sorted=[...fData].sort((a,b)=>{{const c=(a.pf||a.gl||"").localeCompare(b.pf||b.gl||"");if(c!==0)return c;return(pbOrder.indexOf(a.price_band)||999)-(pbOrder.indexOf(b.price_band)||999)}});let rows="";for(const r of sorted){{const st=r.is_insufficient_sample?'<span class="warning">サンプル不足</span>':(r.is_significant?'<span class="success">有意</span>':'<span class="low">非有意</span>');rows+="<tr><td>"+(r.pf||"-")+"</td><td>"+(r.gl||"-")+"</td><td>"+r.price_band+"</td><td>"+r.sample_count.toLocaleString()+"</td><td>"+r.mean_discount.toFixed(1)+"%</td><td>"+r.mean_growth_rate.toFixed(1)+"%</td><td>"+(r.correlation!==null?r.correlation.toFixed(4):"-")+"</td><td>"+(r.regression_coef!==null?r.regression_coef.toFixed(4):"-")+"</td><td>"+st+"</td></tr>"}}document.getElementById("segmentTable").innerHTML="<table><thead><tr><th>PF</th><th>GL</th><th>価格帯</th><th>サンプル数</th><th>平均割引率</th><th>平均伸び率</th><th>相関係数</th><th>回帰係数</th><th>ステータス</th></tr></thead><tbody>"+rows+"</tbody></table>"}}function calcOpt(r,minP,baseP){{if(r.is_insufficient_sample||r.regression_coef===null)return{{opt:r.mean_discount,growth:r.mean_growth_rate,pi:100,conf:"低",note:r.is_insufficient_sample?"サンプル不足":"データなし"}};const coef=r.regression_coef,intercept=r.regression_intercept;const maxD=Math.min(50,Math.max(0,baseP>0?((baseP-minP)/baseP)*100:50));let best=0,bestPI=0,bestG=0;for(let d=0;d<=maxD;d+=0.5){{const g=intercept+coef*d;const pi=(1+g/100)*(1-d/100)*100;if(pi>bestPI){{bestPI=pi;best=d;bestG=g}}}}let conf="低";if(r.is_significant&&r.r_squared>0.3)conf="高";else if(r.is_significant||r.r_squared>0.1)conf="中";let note=coef>0?(best>=maxD-0.5?"利益率制約":"利益最大化"):(coef<0?"割引なし推奨":"関係なし");if(!r.is_significant)note+="(非有意)";return{{opt:Math.round(best*10)/10,growth:Math.round(bestG*100)/100,pi:Math.round(bestPI*100)/100,conf:conf,note:note}}}}function recalc(){{const minP=parseFloat(document.getElementById("minProfit").value)||20;const baseP=parseFloat(document.getElementById("baseProfit").value)||30;const sorted=[...fData].sort((a,b)=>{{const c=(a.pf||a.gl||"").localeCompare(b.pf||b.gl||"");if(c!==0)return c;return(pbOrder.indexOf(a.price_band)||999)-(pbOrder.indexOf(b.price_band)||999)}});let rows="";for(const r of sorted){{const rec=calcOpt(r,minP,baseP);const cc=rec.conf==="高"?"success":(rec.conf==="中"?"warning":"low");const pc=rec.pi>=100?"profit-positive":"profit-negative";rows+='<tr class="'+pc+'"><td>'+(r.pf||"-")+"</td><td>"+(r.gl||"-")+"</td><td>"+r.price_band+"</td><td>"+r.sample_count.toLocaleString()+"</td><td><strong>"+rec.opt.toFixed(1)+"%</strong></td><td>"+rec.growth.toFixed(1)+"%</td><td>"+rec.pi.toFixed(1)+'</td><td><span class="'+cc+'">'+rec.conf+"</span></td><td>"+rec.note+"</td></tr>"}}document.getElementById("recTable").innerHTML="<table><thead><tr><th>PF</th><th>GL</th><th>価格帯</th><th>サンプル数</th><th>推奨割引率</th><th>期待伸び率</th><th>利益指数</th><th>信頼度</th><th>備考</th></tr></thead><tbody>"+rows+"</tbody></table>"}}function renderGl(){{if(!fGl||fGl.length===0){{document.getElementById("glTable").innerHTML="<p>データなし</p>";return}}const sorted=[...fGl].sort((a,b)=>{{if(a.gl!==b.gl)return a.gl.localeCompare(b.gl);const pa=pbOrder.indexOf(a.price_band),pb=pbOrder.indexOf(b.price_band);if(pa!==pb)return(pa===-1?999:pa)-(pb===-1?999:pb);const da=dtOrder.indexOf(a.discount_tier),db=dtOrder.indexOf(b.discount_tier);return(da===-1?999:da)-(db===-1?999:db)}});let rows="";for(const r of sorted){{const gc=r.avg_growth_rate>=0?"profit-positive":"profit-negative";rows+='<tr class="'+gc+'"><td>'+r.gl+"</td><td>"+r.price_band+"</td><td>"+r.discount_tier+"</td><td>"+r.sample_count.toLocaleString()+"</td><td><strong>"+r.avg_growth_rate.toFixed(1)+"%</strong></td><td>"+(r.std_growth_rate?r.std_growth_rate.toFixed(1):"-")+"%</td></tr>"}}document.getElementById("glTable").innerHTML="<table><thead><tr><th>GL</th><th>価格帯</th><th>割引率帯</th><th>サンプル数</th><th>平均伸び率</th><th>標準偏差</th></tr></thead><tbody>"+rows+"</tbody></table>"}}function renderHeatmap(){{if(!fGl||fGl.length===0){{document.getElementById("heatmapChart").innerHTML="<p>データなし</p>";return}}const gls=[...new Set(fGl.map(r=>r.gl))].sort();const pbs=pbOrder.filter(pb=>fGl.some(r=>r.price_band===pb));const z=[];for(const gl of gls){{const row=[];for(const pb of pbs){{const m=fGl.filter(r=>r.gl===gl&&r.price_band===pb);if(m.length>0){{const avg=m.reduce((s,r)=>s+r.avg_growth_rate*r.sample_count,0)/m.reduce((s,r)=>s+r.sample_count,0);row.push(avg)}}else row.push(null)}}z.push(row)}}Plotly.newPlot("heatmapChart",[{{z:z,x:pbs,y:gls,type:"heatmap",colorscale:"RdYlGn",colorbar:{{title:"平均伸び率(%)"}}}}],{{title:"GL×価格帯 平均伸び率",xaxis:{{title:"価格帯"}},yaxis:{{title:"GL"}}}})}}function updateCommand(){{const fp=document.getElementById("newFilePath").value;document.getElementById("cmdDisplay").textContent='python -m src.run_discount_analysis "'+fp+'" --gl'}}document.addEventListener("DOMContentLoaded",renderAll);</script></body></html>"""

class ExcelExporter:
    def export(self, df, analysis_results, recommendations, output_path, gl_price_discount_df=None, max_detail_rows=100000):
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                self._create_summary_df(analysis_results).to_excel(writer, sheet_name='サマリー', index=False)
                if gl_price_discount_df is not None and len(gl_price_discount_df) > 0:
                    gl_price_discount_df.to_excel(writer, sheet_name='GL価格帯割引率', index=False)
                self._create_recommendations_df(recommendations).to_excel(writer, sheet_name='推奨割引率', index=False)
                if len(df) > max_detail_rows:
                    logger.warning(f'詳細データを{max_detail_rows:,}行に制限')
                detail_df = df.head(max_detail_rows).copy()
                cols = ['asin', 'pf', 'gl', 'paid-flag', 'our_price', 'current_discount_percent', 'past_month_gms', 'promotion_ops', 'growth_rate', 'price_band', 'discount_tier']
                detail_df = detail_df[[c for c in cols if c in detail_df.columns]]
                detail_df.to_excel(writer, sheet_name='詳細データ', index=False)
            logger.info(f'Excelファイルを生成: {output_path}')
        except MemoryError:
            logger.error('メモリ不足')
    def _create_summary_df(self, results):
        return pd.DataFrame([{'PF': r.pf, 'GL': r.gl, '価格帯': r.price_band, 'サンプル数': r.sample_count, '平均割引率(%)': r.mean_discount, '平均伸び率(%)': r.mean_growth_rate, '相関係数': r.correlation, '回帰係数': r.regression_coef, 'R²': r.r_squared, 'p値': r.p_value, '統計的有意': '有意' if r.is_significant else '非有意'} for r in results])
    def _create_recommendations_df(self, recommendations):
        return pd.DataFrame([{'PF': r.pf, '価格帯': r.price_band, '推奨割引率(%)': r.optimal_discount_rate, '期待伸び率(%)': r.expected_growth_rate, '信頼度': r.confidence_level, '備考': r.note} for r in recommendations])

class JSONSerializer:
    def serialize(self, results): return json.dumps(results.to_dict(), ensure_ascii=False, indent=2)
    def deserialize(self, json_str): return AnalysisResults.from_dict(json.loads(json_str))
    def save(self, results, output_path):
        with open(output_path, 'w', encoding='utf-8') as f: f.write(self.serialize(results))
        logger.info(f'JSONファイルを保存: {output_path}')
    def load(self, input_path):
        with open(input_path, 'r', encoding='utf-8') as f: return self.deserialize(f.read())
'''

with open('src/discount_report.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Written successfully')
