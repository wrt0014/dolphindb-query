#!/usr/bin/env python3
"""
DolphinDB 查询辅助工具
用于查询和分析 DolphinDB 中的金融数据
"""

import dolphindb as ddb
from typing import Optional, List, Dict, Any
import pandas as pd


class DolphinDBHelper:
    """DolphinDB 查询辅助类"""

    def __init__(self, host: str = "124.222.92.184", port: int = 8848,
                 username: str = "admin", password: str = "66583456@*"):
        """
        初始化连接

        Args:
            host: DolphinDB 服务器地址
            port: 端口
            username: 用户名
            password: 密码
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.session: Optional[ddb.Session] = None

    def connect(self) -> bool:
        """建立连接"""
        try:
            self.session = ddb.Session()
            self.session.connect(self.host, self.port, self.username, self.password)
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def execute(self, sql: str) -> Optional[pd.DataFrame]:
        """
        执行 SQL 查询

        Args:
            sql: DolphinDB SQL 语句

        Returns:
            查询结果 DataFrame，失败返回 None
        """
        if not self.session:
            if not self.connect():
                return None

        try:
            result = self.session.run(sql)
            if result is not None:
                return result.toDF()
            return pd.DataFrame()
        except Exception as e:
            print(f"查询执行失败: {e}")
            print(f"SQL: {sql}")
            return None

    def query_fund_by_name(self, keyword: str) -> Optional[pd.DataFrame]:
        """根据名称关键字查询基金"""
        sql = f"""
        select _id, name, scale, benchmark, manager, start_date, end_date,
               benchmark_index_id, peer_group_id, current_manager_id
        from Fund
        where name like '%{keyword}%'
        """
        return self.execute(sql)

    def query_fund_holdings(self, fund_id: str, date: str = None) -> Optional[pd.DataFrame]:
        """查询基金持仓"""
        date_filter = f"and ph.date = '{date}'" if date else ""
        sql = f"""
        select ph.asset_id, ss.name as stock_name, ss.code,
               ph.weight, ph.date, ph.exposure_value
        from portfolio_holding ph
        join Security_Stock ss on ph.asset_id = ss._id
        where ph.holder_id = '{fund_id}' {date_filter}
        order by ph.weight desc
        """
        return self.execute(sql)

    def query_fund_performance(self, fund_id: str, metric_name: str = None) -> Optional[pd.DataFrame]:
        """查询基金业绩"""
        metric_filter = f"and pm.name like '%{metric_name}%'" if metric_name else ""
        sql = f"""
        select f.name as fund_name, pm.name as metric_name,
               fpf.value, fpf.date, pm.metric_type
        from fund_performance_fact fpf
        join Fund f on fpf.fund_id = f._id
        join Performance_Metric pm on fpf.performance_metric_id = pm._id
        where f._id = '{fund_id}' {metric_filter}
        order by fpf.date desc
        """
        return self.execute(sql)

    def query_stock_by_name(self, keyword: str) -> Optional[pd.DataFrame]:
        """根据名称或代码查询股票"""
        sql = f"""
        select _id, name, code, market, exchange, ipo_date, issuer_company_id
        from Security_Stock
        where name like '%{keyword}%' or code like '%{keyword}%'
        """
        return self.execute(sql)

    def query_stock_industry(self, stock_id: str) -> Optional[pd.DataFrame]:
        """查询股票所属行业"""
        sql = f"""
        select ss.name as stock_name, ss.code,
               il.name as industry_l1, il.code as industry_code,
               sim.date
        from Security_Stock ss
        join stock_industry_membership sim on ss._id = sim.stock_id
        join Industry_L1 il on sim.industry_l1_id = il._id
        where ss._id = '{stock_id}'
        order by sim.date desc
        """
        return self.execute(sql)

    def query_stock_style_exposure(self, stock_id: str) -> Optional[pd.DataFrame]:
        """查询股票风格暴露"""
        sql = f"""
        select ss.name as stock_name, sf.name as style_factor,
               sse.actual_value, sse.date
        from Security_Stock ss
        join stock_style_exposure sse on ss._id = sse.stock_id
        join Style_Factor sf on sse.style_factor_id = sf._id
        where ss._id = '{stock_id}'
        order by sse.date desc
        """
        return self.execute(sql)

    def query_manager_by_name(self, keyword: str) -> Optional[pd.DataFrame]:
        """根据名称查询基金经理"""
        sql = f"""
        select _id, name, expertise, start_date, end_date
        from Manager
        where name like '%{keyword}%'
        """
        return self.execute(sql)

    def query_manager_funds(self, manager_id: str, current_only: bool = True) -> Optional[pd.DataFrame]:
        """查询经理管理的基金"""
        current_filter = "and mft.is_current = 'true'" if current_only else ""
        sql = f"""
        select m.name as manager_name, f.name as fund_name, f._id as fund_id,
               mft.start_date, mft.end_date, mft.is_current
        from Manager m
        join manager_fund_tenure mft on m._id = mft.manager_id
        join Fund f on mft.fund_id = f._id
        where m._id = '{manager_id}' {current_filter}
        order by mft.start_date desc
        """
        return self.execute(sql)

    def query_peer_group_funds(self, peer_group_id: str) -> Optional[pd.DataFrame]:
        """查询同类组所有基金"""
        sql = f"""
        select f._id, f.name, f.scale, pg.name as peer_group_name
        from Fund f
        join Peer_Group pg on f.peer_group_id = pg._id
        where pg._id = '{peer_group_id}'
        """
        return self.execute(sql)

    def query_stocks_by_industry(self, industry_l1_id: str) -> Optional[pd.DataFrame]:
        """查询某行业的所有股票"""
        sql = f"""
        select distinct ss._id, ss.name, ss.code, il.name as industry
        from Security_Stock ss
        join stock_industry_membership sim on ss._id = sim.stock_id
        join Industry_L1 il on sim.industry_l1_id = il._id
        where il._id = '{industry_l1_id}'
        """
        return self.execute(sql)

    def query_top_funds_by_metric(self, metric_name: str, top_n: int = 10) -> Optional[pd.DataFrame]:
        """查询某指标排名前N的基金"""
        sql = f"""
        select top {top_n} f.name as fund_name, fpf.value, fpf.date,
               pm.name as metric_name, pm.metric_type
        from fund_performance_fact fpf
        join Fund f on fpf.fund_id = f._id
        join Performance_Metric pm on fpf.performance_metric_id = pm._id
        where pm.name like '%{metric_name}%'
        order by cast(fpf.value as double) desc
        """
        return self.execute(sql)

    def close(self):
        """关闭连接"""
        if self.session:
            self.session.close()


# 便捷函数
def query_dolphindb(sql: str) -> Optional[pd.DataFrame]:
    """单次查询便捷函数"""
    helper = DolphinDBHelper()
    result = helper.execute(sql)
    helper.close()
    return result


if __name__ == "__main__":
    # 测试连接
    helper = DolphinDBHelper()
    if helper.connect():
        print("连接成功！")

        # 测试查询基金
        print("\n=== 查询基金示例 ===")
        funds = helper.query_fund_by_name("华夏")
        if funds is not None:
            print(funds.head())

        helper.close()
