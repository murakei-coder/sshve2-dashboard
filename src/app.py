"""
Streamlit Dashboard for Deal Sourcing Analyzer.
Main entry point for the web application.
"""
import streamlit as st
import pandas as pd

from src.file_loader import FileLoader
from src.data_parser import DataParser, ValidationError
from src.analyzer import Analyzer
from src.large_file_loader import load_large_file


def main():
    """Main entry point for the Streamlit dashboard."""
    st.set_page_config(
        page_title="Deal Sourcing Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Deal Sourcing Analyzer")
    st.markdown("3Pセラーのディールエントリー状況を分析するダッシュボード")
    
    # Initialize components
    file_loader = FileLoader(data_dir="data")
    data_parser = DataParser()
    
    # File selection
    available_files = file_loader.list_available_files()
    
    if not available_files:
        st.warning("⚠️ dataフォルダにtxtファイルが見つかりません。分析対象のファイルを配置してください。")
        return
    
    selected_file = st.selectbox(
        "📁 分析対象ファイルを選択",
        options=available_files,
        help="dataフォルダ内のtxtファイルから選択してください"
    )
    
    # Large file option
    use_chunked = st.checkbox("大容量ファイルモード（800万行以上推奨）", value=False)
    
    # Analysis button
    if st.button("🔍 分析開始", type="primary"):
        # Clear previous session state
        if 'analyzer' in st.session_state:
            del st.session_state['analyzer']
        if 'df' in st.session_state:
            del st.session_state['df']
        
        try:
            if use_chunked:
                # Large file mode: aggregate while reading using separate module
                with st.spinner("データを集計中...（大容量ファイルの場合は数分かかります）"):
                    file_path = file_loader.data_dir / selected_file
                    agg_data = load_large_file(str(file_path), chunksize=100000)
                
                st.success(f"✅ {agg_data['total_rows']:,}件のデータを集計しました")
                new_analyzer = Analyzer(agg_data)
                st.session_state['analyzer'] = new_analyzer
            else:
                # Normal mode: load entire file
                with st.spinner("データを読み込み中..."):
                    df = file_loader.load_file(selected_file)
                    df = data_parser.parse_and_validate(df)
                
                st.success(f"✅ {len(df):,}件のデータを読み込みました")
                st.session_state['df'] = df
                new_analyzer = Analyzer(df)
                st.session_state['analyzer'] = new_analyzer
            
        except FileNotFoundError as e:
            st.error(f"❌ ファイルが見つかりません: {e}")
        except ValidationError as e:
            st.error(f"❌ データ検証エラー: {e}")
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
    
    # Display analysis if data is loaded
    if 'analyzer' in st.session_state:
        analyzer = st.session_state['analyzer']
        display_dashboard(analyzer)



def display_dashboard(analyzer: Analyzer):
    """Display the full analysis dashboard."""
    display_summary(analyzer)
    display_insights(analyzer)
    display_detailed_statistics(analyzer)
    display_paid_analysis(analyzer)
    display_price_band_analysis(analyzer)
    display_tenure_analysis(analyzer)


def display_summary(analyzer: Analyzer):
    """Display overall summary metrics with Paid vs NonPaid comparison."""
    st.header("📈 サマリー（Paid vs NonPaid比較）")
    
    summary = analyzer.get_summary()
    paid_df = analyzer.analyze_by_paid_flag()
    
    # 全体サマリー
    st.subheader("📊 全体")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("総GMS", f"¥{summary.total_gms:,.0f}")
    with col2:
        st.metric("総ASIN数", f"{summary.total_asin_count:,}")
    with col3:
        st.metric("総Opportunity", f"¥{summary.total_opportunity_gms:,.0f}")
    
    # Paid vs NonPaid 比較表
    st.subheader("🔄 Paid vs NonPaid 比較")
    
    if len(paid_df) >= 2:
        paid_row = paid_df[paid_df['paid-flag'] == 'Y'].iloc[0] if len(paid_df[paid_df['paid-flag'] == 'Y']) > 0 else None
        nonpaid_row = paid_df[paid_df['paid-flag'] == 'N'].iloc[0] if len(paid_df[paid_df['paid-flag'] == 'N']) > 0 else None
        
        if paid_row is not None and nonpaid_row is not None:
            # 比較表データ作成
            comparison_data = {
                '指標': [
                    '総GMS',
                    'ASIN数',
                    'Sourced GMS',
                    'NonSourced GMS (Opportunity)',
                    'Sourced率 (GMS%)',
                    'Sourced率 (ASIN%)',
                    'GMS/ASIN',
                    'Sourced ASIN数',
                    'NonSourced ASIN数'
                ],
                'Paid': [
                    f"¥{paid_row['total_gms']:,.0f}",
                    f"{paid_row['total_asin_count']:,}",
                    f"¥{paid_row['sourced_gms']:,.0f}",
                    f"¥{paid_row['nonsourced_gms']:,.0f}",
                    f"{paid_row['sourced_rate_gms_weighted']:.1%}",
                    f"{paid_row['sourced_rate']:.1%}",
                    f"¥{paid_row['gms_per_asin']:,.0f}",
                    f"{paid_row['sourced_asin_count']:,}",
                    f"{paid_row['nonsourced_asin_count']:,}"
                ],
                'NonPaid': [
                    f"¥{nonpaid_row['total_gms']:,.0f}",
                    f"{nonpaid_row['total_asin_count']:,}",
                    f"¥{nonpaid_row['sourced_gms']:,.0f}",
                    f"¥{nonpaid_row['nonsourced_gms']:,.0f}",
                    f"{nonpaid_row['sourced_rate_gms_weighted']:.1%}",
                    f"{nonpaid_row['sourced_rate']:.1%}",
                    f"¥{nonpaid_row['gms_per_asin']:,.0f}",
                    f"{nonpaid_row['sourced_asin_count']:,}",
                    f"{nonpaid_row['nonsourced_asin_count']:,}"
                ],
                '差分 (Paid - NonPaid)': [
                    f"¥{paid_row['total_gms'] - nonpaid_row['total_gms']:+,.0f}",
                    f"{paid_row['total_asin_count'] - nonpaid_row['total_asin_count']:+,}",
                    f"¥{paid_row['sourced_gms'] - nonpaid_row['sourced_gms']:+,.0f}",
                    f"¥{paid_row['nonsourced_gms'] - nonpaid_row['nonsourced_gms']:+,.0f}",
                    f"{(paid_row['sourced_rate_gms_weighted'] - nonpaid_row['sourced_rate_gms_weighted'])*100:+.1f}pt",
                    f"{(paid_row['sourced_rate'] - nonpaid_row['sourced_rate'])*100:+.1f}pt",
                    f"¥{paid_row['gms_per_asin'] - nonpaid_row['gms_per_asin']:+,.0f}",
                    f"{paid_row['sourced_asin_count'] - nonpaid_row['sourced_asin_count']:+,}",
                    f"{paid_row['nonsourced_asin_count'] - nonpaid_row['nonsourced_asin_count']:+,}"
                ]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            
            st.dataframe(
                comparison_df,
                column_config={
                    '指標': st.column_config.TextColumn('指標', width='medium'),
                    'Paid': st.column_config.TextColumn('Paid', width='medium'),
                    'NonPaid': st.column_config.TextColumn('NonPaid', width='medium'),
                    '差分 (Paid - NonPaid)': st.column_config.TextColumn('差分', width='medium')
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Paidチームの状況サマリー
            gms_rate_diff = paid_row['sourced_rate_gms_weighted'] - nonpaid_row['sourced_rate_gms_weighted']
            if gms_rate_diff > 0:
                st.success(f"✅ PaidチームはNonPaidよりSourced率(GMS%)が {gms_rate_diff*100:.1f}pt 高い状況です")
            elif gms_rate_diff < 0:
                st.warning(f"⚠️ PaidチームはNonPaidよりSourced率(GMS%)が {abs(gms_rate_diff)*100:.1f}pt 低い状況です")
            else:
                st.info("ℹ️ PaidとNonPaidのSourced率(GMS%)は同等です")
    else:
        st.info("Paid/NonPaidの比較データがありません")
    
    st.divider()


def display_insights(analyzer: Analyzer):
    """Display actionable insights based on analysis - Paid Team perspective (GMS% based)."""
    st.header("💡 Paidチーム向け示唆・アクションポイント")
    st.caption("※ソーシング率はすべてGMS%ベース（総GMSのうち何%をソーシングできているか）で表示")
    
    summary = analyzer.get_summary()
    paid_df = analyzer.analyze_by_paid_flag()
    price_df = analyzer.analyze_by_price_band()
    tenure_df = analyzer.analyze_by_tenure()
    price_stats = analyzer.get_price_statistics()
    corr = analyzer.get_correlation_analysis()
    
    insights = []
    
    # Paid vs Non-Paid comparison (Paid Team perspective - GMS% based)
    if len(paid_df) >= 1:
        paid_row = paid_df[paid_df['paid-flag'] == 'Y'].iloc[0] if len(paid_df[paid_df['paid-flag'] == 'Y']) > 0 else None
        nonpaid_row = paid_df[paid_df['paid-flag'] == 'N'].iloc[0] if len(paid_df[paid_df['paid-flag'] == 'N']) > 0 else None
        
        if paid_row is not None and nonpaid_row is not None:
            # Paidチームの強み・弱み（GMS%ベース）
            strengths = []
            weaknesses = []
            
            # Sourced率比較 (GMS Weighted のみ)
            paid_gms_rate = paid_row['sourced_rate_gms_weighted']
            nonpaid_gms_rate = nonpaid_row['sourced_rate_gms_weighted']
            gms_rate_diff = paid_gms_rate - nonpaid_gms_rate
            
            if gms_rate_diff > 0.02:
                strengths.append(f"Sourced率(GMS%): Paid {paid_gms_rate:.1%} vs NonPaid {nonpaid_gms_rate:.1%} (+{gms_rate_diff:.1%})")
            elif gms_rate_diff < -0.02:
                weaknesses.append(f"Sourced率(GMS%): Paid {paid_gms_rate:.1%} vs NonPaid {nonpaid_gms_rate:.1%} ({gms_rate_diff:.1%})")
            
            # GMS/ASIN比較
            gms_asin_diff = paid_row['gms_per_asin'] - nonpaid_row['gms_per_asin']
            if gms_asin_diff > 0:
                strengths.append(f"GMS/ASIN: Paid ¥{paid_row['gms_per_asin']:,.0f} vs NonPaid ¥{nonpaid_row['gms_per_asin']:,.0f} (+¥{gms_asin_diff:,.0f})")
            else:
                weaknesses.append(f"GMS/ASIN: Paid ¥{paid_row['gms_per_asin']:,.0f} vs NonPaid ¥{nonpaid_row['gms_per_asin']:,.0f} (¥{gms_asin_diff:,.0f})")
            
            # Opportunity比較
            total_opp = paid_row['opportunity_gms'] + nonpaid_row['opportunity_gms']
            opp_ratio = paid_row['opportunity_gms'] / total_opp if total_opp > 0 else 0
            
            if strengths:
                insights.append({
                    'type': 'success',
                    'title': '🏆 Paidチームの強み（vs NonPaid）',
                    'message': '\n'.join([f"• {s}" for s in strengths]),
                    'action': 'Paidチームとしてこれらの強みを維持・強化し、NonPaidとの差別化を継続してください。'
                })
            
            if weaknesses:
                insights.append({
                    'type': 'warning',
                    'title': '⚠️ Paidチームの改善ポイント（vs NonPaid）',
                    'message': '\n'.join([f"• {w}" for w in weaknesses]),
                    'action': 'Paidチームとして、NonPaidに劣後している領域の原因分析と改善策を検討してください。Paidセラーへの働きかけを強化する必要があります。'
                })
            
            # Paid Opportunity
            insights.append({
                'type': 'info',
                'title': f"💰 PaidチームのOpportunity: ¥{paid_row['opportunity_gms']:,.0f}",
                'message': f"全体Opportunityの{opp_ratio:.1%}がPaidセラーに存在します。\nPaid NonSourced ASIN数: {paid_row['nonsourced_asin_count']:,}件\nPaid Sourced率(GMS%): {paid_gms_rate:.1%}",
                'action': f"Paidチームとして、Paid NonSourced ASINへのディールエントリーを推進することで¥{paid_row['opportunity_gms']:,.0f}のGMS獲得が見込めます。"
            })
    
    # 3. Price Band Insight (Paid Team perspective, GMS% based)
    if len(price_df) > 0:
        scored_price = analyzer.calculate_opportunity_score(price_df)
        high_opp_price = scored_price[scored_price['opportunity_level'] == '高']
        
        if len(high_opp_price) > 0:
            top_opp = high_opp_price.nlargest(1, 'opportunity_gms').iloc[0]
            insights.append({
                'type': 'warning',
                'title': f"【Paidチーム注目】価格帯「{top_opp['priceband']}」に大きなOpportunity",
                'message': f"この価格帯はSourced率(GMS%) {top_opp['sourced_rate_gms_weighted']:.1%}で、¥{top_opp['opportunity_gms']:,.0f}のOpportunityがあります。",
                'action': 'Paidチームとして、この価格帯のPaidセラーASINに優先的にアプローチすることで効率的にGMSを獲得できます。'
            })
        
        # High GMS per ASIN segments
        if len(scored_price) > 0:
            high_gms_asin = scored_price.nlargest(1, 'gms_per_asin').iloc[0]
            if high_gms_asin['sourced_rate_gms_weighted'] < 0.8:
                insights.append({
                    'type': 'info',
                    'title': f"【Paidチーム注目】高単価セグメント「{high_gms_asin['priceband']}」",
                    'message': f"GMS/ASINが¥{high_gms_asin['gms_per_asin']:,.0f}と高く、1ASINあたりのGMS貢献度が大きいです。Sourced率(GMS%): {high_gms_asin['sourced_rate_gms_weighted']:.1%}",
                    'action': 'Paidチームとして、このセグメントのPaid NonSourced ASINを優先的にディールエントリーすることで効率的にGMSを伸ばせます。'
                })
    
    # 4. Tenure Insight (Paid Team perspective, GMS% based)
    if len(tenure_df) > 0:
        scored_tenure = analyzer.calculate_opportunity_score(tenure_df)
        high_opp_tenure = scored_tenure[scored_tenure['opportunity_level'] == '高']
        
        if len(high_opp_tenure) > 0:
            top_tenure = high_opp_tenure.nlargest(1, 'opportunity_gms').iloc[0]
            insights.append({
                'type': 'warning',
                'title': f"【Paidチーム注目】出品期間「{top_tenure['asintenure']}」に大きなOpportunity",
                'message': f"この期間のASINはSourced率(GMS%) {top_tenure['sourced_rate_gms_weighted']:.1%}で、¥{top_tenure['opportunity_gms']:,.0f}のOpportunityがあります。",
                'action': 'Paidチームとして、この出品期間のPaidセラーASINへのアプローチを強化してください。'
            })
    
    # 5. Price Statistics Insight (Paid Team perspective)
    if len(price_stats) == 2:
        sourced_price = price_stats[price_stats['status'] == 'Sourced']
        nonsourced_price = price_stats[price_stats['status'] == 'NonSourced']
        
        if len(sourced_price) > 0 and len(nonsourced_price) > 0:
            sourced_mean = sourced_price.iloc[0]['price_mean']
            nonsourced_mean = nonsourced_price.iloc[0]['price_mean']
            
            if nonsourced_mean > sourced_mean * 1.2:
                insights.append({
                    'type': 'info',
                    'title': '【Paidチーム課題】NonSourcedは高価格帯に集中',
                    'message': f"NonSourcedの平均価格(¥{nonsourced_mean:,.0f})はSourced(¥{sourced_mean:,.0f})より高いです。高価格帯のGMSを取りこぼしている可能性があります。",
                    'action': 'Paidチームとして、高価格帯Paidセラーへのディールエントリー障壁を分析してください。価格設定やマージンの問題がある可能性があります。'
                })
            elif sourced_mean > nonsourced_mean * 1.2:
                insights.append({
                    'type': 'success',
                    'title': '【Paidチーム強み】高価格帯のSourced率が高い',
                    'message': f"Sourcedの平均価格(¥{sourced_mean:,.0f})がNonSourced(¥{nonsourced_mean:,.0f})より高く、高価格帯でのディールエントリーが進んでいます。",
                    'action': 'Paidチームとして、この強みを維持しつつ、低価格帯Paidセラーへのディールエントリー促進も検討してください。'
                })
    
    # 6. Correlation Insight with interpretation (Paid Team perspective)
    # 相関係数の解釈を追加
    def interpret_correlation(corr_value, var1, var2):
        """相関係数の強さと方向を解釈"""
        abs_corr = abs(corr_value)
        if abs_corr < 0.1:
            strength = "ほぼ無相関"
        elif abs_corr < 0.3:
            strength = "弱い相関"
        elif abs_corr < 0.5:
            strength = "中程度の相関"
        elif abs_corr < 0.7:
            strength = "強い相関"
        else:
            strength = "非常に強い相関"
        
        direction = "正" if corr_value > 0 else "負"
        return strength, direction
    
    # Price-GMS correlation
    price_gms_strength, price_gms_dir = interpret_correlation(corr['price_gms_corr'], '価格', 'GMS')
    if abs(corr['price_gms_corr']) >= 0.1:
        if corr['price_gms_corr'] > 0:
            interpretation = f"価格が高いほどGMSが大きい傾向（{price_gms_strength}）"
            action = "Paidチームとして、高価格帯PaidセラーASINへの注力がGMS向上に効果的です。"
        else:
            interpretation = f"価格が低いほどGMSが大きい傾向（{price_gms_strength}）"
            action = "Paidチームとして、低価格帯PaidセラーASINの数量確保がGMS向上に効果的です。"
        
        insights.append({
            'type': 'info',
            'title': f"【相関分析】価格とGMSの関係: {price_gms_dir}の{price_gms_strength}",
            'message': f"相関係数: {corr['price_gms_corr']:.3f}\n{interpretation}",
            'action': action
        })
    
    # Tenure-GMS correlation
    tenure_gms_strength, tenure_gms_dir = interpret_correlation(corr['tenure_gms_corr'], '出品期間', 'GMS')
    if abs(corr['tenure_gms_corr']) >= 0.1:
        if corr['tenure_gms_corr'] > 0:
            interpretation = f"出品期間が長いほどGMSが大きい傾向（{tenure_gms_strength}）"
            action = "Paidチームとして、長期出品PaidセラーASINは安定したGMS貢献が期待できます。"
        else:
            interpretation = f"出品期間が短いほどGMSが大きい傾向（{tenure_gms_strength}）"
            action = "Paidチームとして、新規出品PaidセラーASINへの早期アプローチがGMS向上に効果的です。"
        
        insights.append({
            'type': 'info',
            'title': f"【相関分析】出品期間とGMSの関係: {tenure_gms_dir}の{tenure_gms_strength}",
            'message': f"相関係数: {corr['tenure_gms_corr']:.3f}\n{interpretation}",
            'action': action
        })
    
    # Display insights
    if not insights:
        st.info("現在のデータからは特筆すべき示唆はありません。")
    else:
        for insight in insights:
            if insight['type'] == 'warning':
                st.warning(f"⚠️ **{insight['title']}**\n\n{insight['message']}\n\n**推奨アクション:** {insight['action']}")
            elif insight['type'] == 'success':
                st.success(f"✅ **{insight['title']}**\n\n{insight['message']}\n\n**推奨アクション:** {insight['action']}")
            else:
                st.info(f"ℹ️ **{insight['title']}**\n\n{insight['message']}\n\n**推奨アクション:** {insight['action']}")
    
    st.divider()


def display_detailed_statistics(analyzer: Analyzer):
    """Display detailed price and tenure statistics."""
    st.header("📊 詳細統計分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 価格統計 (our_price)")
        price_stats = analyzer.get_price_statistics()
        if len(price_stats) > 0:
            display_price = price_stats.copy()
            display_price['price_mean'] = display_price['price_mean'].apply(lambda x: f"¥{x:,.0f}")
            display_price['price_median'] = display_price['price_median'].apply(lambda x: f"¥{x:,.0f}")
            display_price['price_std'] = display_price['price_std'].apply(lambda x: f"¥{x:,.0f}")
            display_price['price_min'] = display_price['price_min'].apply(lambda x: f"¥{x:,.0f}")
            display_price['price_max'] = display_price['price_max'].apply(lambda x: f"¥{x:,.0f}")
            
            st.dataframe(
                display_price[['status', 'count', 'price_mean', 'price_median', 'price_std', 'price_min', 'price_max']],
                column_config={
                    'status': 'ステータス',
                    'count': '件数',
                    'price_mean': '平均価格',
                    'price_median': '中央値',
                    'price_std': '標準偏差',
                    'price_min': '最小',
                    'price_max': '最大'
                },
                hide_index=True,
                use_container_width=True
            )
    
    with col2:
        st.subheader("📅 出品期間統計 (asin_tenure_days)")
        tenure_stats = analyzer.get_tenure_statistics()
        if len(tenure_stats) > 0:
            display_tenure = tenure_stats.copy()
            display_tenure['tenure_mean'] = display_tenure['tenure_mean'].apply(lambda x: f"{x:,.0f}日")
            display_tenure['tenure_median'] = display_tenure['tenure_median'].apply(lambda x: f"{x:,.0f}日")
            display_tenure['tenure_std'] = display_tenure['tenure_std'].apply(lambda x: f"{x:,.0f}日")
            display_tenure['tenure_min'] = display_tenure['tenure_min'].apply(lambda x: f"{x:,.0f}日")
            display_tenure['tenure_max'] = display_tenure['tenure_max'].apply(lambda x: f"{x:,.0f}日")
            
            st.dataframe(
                display_tenure[['status', 'count', 'tenure_mean', 'tenure_median', 'tenure_std', 'tenure_min', 'tenure_max']],
                column_config={
                    'status': 'ステータス',
                    'count': '件数',
                    'tenure_mean': '平均日数',
                    'tenure_median': '中央値',
                    'tenure_std': '標準偏差',
                    'tenure_min': '最小',
                    'tenure_max': '最大'
                },
                hide_index=True,
                use_container_width=True
            )
    
    # Correlation analysis with interpretation
    st.subheader("🔗 相関分析")
    corr = analyzer.get_correlation_analysis()
    
    def get_corr_interpretation(corr_value):
        """相関係数の解釈を返す"""
        abs_corr = abs(corr_value)
        if abs_corr < 0.1:
            return "ほぼ無相関", "gray"
        elif abs_corr < 0.3:
            return "弱い相関", "orange"
        elif abs_corr < 0.5:
            return "中程度の相関", "blue"
        elif abs_corr < 0.7:
            return "強い相関", "green"
        else:
            return "非常に強い相関", "red"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        interp, _ = get_corr_interpretation(corr['price_gms_corr'])
        direction = "正" if corr['price_gms_corr'] > 0 else "負"
        st.metric("価格 × GMS 相関", f"{corr['price_gms_corr']:.3f}")
        st.caption(f"{direction}の{interp}：価格が{'高い' if corr['price_gms_corr'] > 0 else '低い'}ほどGMSが大きい")
    with col2:
        interp, _ = get_corr_interpretation(corr['tenure_gms_corr'])
        direction = "正" if corr['tenure_gms_corr'] > 0 else "負"
        st.metric("出品期間 × GMS 相関", f"{corr['tenure_gms_corr']:.3f}")
        st.caption(f"{direction}の{interp}：出品期間が{'長い' if corr['tenure_gms_corr'] > 0 else '短い'}ほどGMSが大きい")
    with col3:
        interp, _ = get_corr_interpretation(corr['price_tenure_corr'])
        direction = "正" if corr['price_tenure_corr'] > 0 else "負"
        st.metric("価格 × 出品期間 相関", f"{corr['price_tenure_corr']:.3f}")
        st.caption(f"{direction}の{interp}：価格が{'高い' if corr['price_tenure_corr'] > 0 else '低い'}ほど出品期間が長い")
    
    st.divider()


def display_paid_analysis(analyzer: Analyzer):
    """Display Paid/Non-Paid seller analysis."""
    st.header("💰 Paid/Non-Paid セラー分析")
    
    paid_df = analyzer.analyze_by_paid_flag()
    
    if len(paid_df) == 0:
        st.info("データがありません")
        return
    
    # Display table
    display_df = paid_df.copy()
    display_df['paid-flag'] = display_df['paid-flag'].map({'Y': 'Paid', 'N': 'Non-Paid'})
    display_df['sourced_rate_display'] = display_df['sourced_rate'].apply(lambda x: f"{x:.1%}")
    display_df['sourced_rate_gms_display'] = display_df['sourced_rate_gms_weighted'].apply(lambda x: f"{x:.1%}")
    display_df['total_gms'] = display_df['total_gms'].apply(lambda x: f"¥{x:,.0f}")
    display_df['opportunity_gms'] = display_df['opportunity_gms'].apply(lambda x: f"¥{x:,.0f}")
    display_df['gms_per_asin'] = display_df['gms_per_asin'].apply(lambda x: f"¥{x:,.0f}")
    
    st.dataframe(
        display_df[['paid-flag', 'total_gms', 'total_asin_count', 'sourced_rate_display', 'sourced_rate_gms_display', 'opportunity_gms', 'gms_per_asin']],
        column_config={
            'paid-flag': 'セラータイプ',
            'total_gms': '総GMS',
            'total_asin_count': 'ASIN数',
            'sourced_rate_display': 'Sourced率(ASIN)',
            'sourced_rate_gms_display': 'Sourced率(GMS)',
            'opportunity_gms': 'Opportunity',
            'gms_per_asin': 'GMS/ASIN'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Bar chart
    col1, col2 = st.columns(2)
    
    with col1:
        chart_df = paid_df.copy()
        chart_df['paid-flag'] = chart_df['paid-flag'].map({'Y': 'Paid', 'N': 'Non-Paid'})
        st.bar_chart(chart_df.set_index('paid-flag')[['sourced_gms', 'nonsourced_gms']])
        st.caption("Sourced/NonSourced GMS比較")
    
    with col2:
        st.bar_chart(chart_df.set_index('paid-flag')[['sourced_asin_count', 'nonsourced_asin_count']])
        st.caption("Sourced/NonSourced ASIN数比較")
    
    st.divider()



def display_price_band_analysis(analyzer: Analyzer):
    """Display Price Band analysis."""
    st.header("💵 Price Band分析")
    
    price_df = analyzer.analyze_by_price_band()
    
    if len(price_df) == 0:
        st.info("データがありません")
        return
    
    # Add opportunity scores
    scored_df = analyzer.calculate_opportunity_score(price_df)
    
    # Display table with highlighting
    display_df = scored_df.copy()
    display_df['sourced_rate_display'] = display_df['sourced_rate'].apply(lambda x: f"{x:.1%}")
    display_df['sourced_rate_gms_display'] = display_df['sourced_rate_gms_weighted'].apply(lambda x: f"{x:.1%}")
    display_df['opportunity_ratio'] = display_df['opportunity_ratio'].apply(lambda x: f"{x:.1%}")
    display_df['total_gms'] = display_df['total_gms'].apply(lambda x: f"¥{x:,.0f}")
    display_df['opportunity_gms'] = display_df['opportunity_gms'].apply(lambda x: f"¥{x:,.0f}")
    display_df['gms_per_asin'] = display_df['gms_per_asin'].apply(lambda x: f"¥{x:,.0f}")
    
    st.dataframe(
        display_df[['priceband', 'total_gms', 'total_asin_count', 'sourced_rate_display', 'sourced_rate_gms_display',
                   'opportunity_gms', 'opportunity_ratio', 'gms_per_asin', 'opportunity_level']],
        column_config={
            'priceband': '価格帯',
            'total_gms': '総GMS',
            'total_asin_count': 'ASIN数',
            'sourced_rate_display': 'Sourced率(ASIN)',
            'sourced_rate_gms_display': 'Sourced率(GMS)',
            'opportunity_gms': 'Opportunity',
            'opportunity_ratio': 'Opportunity比率',
            'gms_per_asin': 'GMS/ASIN',
            'opportunity_level': 'Opportunity判定'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Highlight high opportunity segments
    high_opp = scored_df[scored_df['opportunity_level'] == '高']
    if len(high_opp) > 0:
        st.success(f"🎯 高Opportunityセグメント: {', '.join(high_opp['priceband'].tolist())}")
    
    # Bar chart
    st.bar_chart(scored_df.set_index('priceband')[['sourced_gms', 'nonsourced_gms']])
    st.caption("価格帯別 Sourced/NonSourced GMS")
    
    st.divider()



def display_tenure_analysis(analyzer: Analyzer):
    """Display ASIN Tenure analysis."""
    st.header("📅 ASIN Tenure分析")
    
    tenure_df = analyzer.analyze_by_tenure()
    
    if len(tenure_df) == 0:
        st.info("データがありません")
        return
    
    # Add opportunity scores
    scored_df = analyzer.calculate_opportunity_score(tenure_df)
    
    # Display table with highlighting
    display_df = scored_df.copy()
    display_df['sourced_rate_display'] = display_df['sourced_rate'].apply(lambda x: f"{x:.1%}")
    display_df['sourced_rate_gms_display'] = display_df['sourced_rate_gms_weighted'].apply(lambda x: f"{x:.1%}")
    display_df['opportunity_ratio'] = display_df['opportunity_ratio'].apply(lambda x: f"{x:.1%}")
    display_df['total_gms'] = display_df['total_gms'].apply(lambda x: f"¥{x:,.0f}")
    display_df['opportunity_gms'] = display_df['opportunity_gms'].apply(lambda x: f"¥{x:,.0f}")
    display_df['gms_per_asin'] = display_df['gms_per_asin'].apply(lambda x: f"¥{x:,.0f}")
    
    st.dataframe(
        display_df[['asintenure', 'total_gms', 'total_asin_count', 'sourced_rate_display', 'sourced_rate_gms_display',
                   'opportunity_gms', 'opportunity_ratio', 'gms_per_asin', 'opportunity_level']],
        column_config={
            'asintenure': '出品期間',
            'total_gms': '総GMS',
            'total_asin_count': 'ASIN数',
            'sourced_rate_display': 'Sourced率(ASIN)',
            'sourced_rate_gms_display': 'Sourced率(GMS)',
            'opportunity_gms': 'Opportunity',
            'opportunity_ratio': 'Opportunity比率',
            'gms_per_asin': 'GMS/ASIN',
            'opportunity_level': 'Opportunity判定'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Highlight high opportunity segments
    high_opp = scored_df[scored_df['opportunity_level'] == '高']
    if len(high_opp) > 0:
        st.success(f"🎯 高Opportunityセグメント: {', '.join(high_opp['asintenure'].tolist())}")
    
    # Strong ASIN segments
    strong_asin = scored_df[scored_df['strong_asin'] == True]
    if len(strong_asin) > 0:
        st.info(f"💪 強いASINセグメント (高GMS/ASIN): {', '.join(strong_asin['asintenure'].tolist())}")
    
    # Bar chart
    st.bar_chart(scored_df.set_index('asintenure')[['sourced_gms', 'nonsourced_gms']])
    st.caption("出品期間別 Sourced/NonSourced GMS")


if __name__ == "__main__":
    main()
