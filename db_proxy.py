'''==================================================
@IDE: PyCharm
@Time : 2021/9/10 14:49
@Author : wyp
@File : db_proxy.py
=================================================='''
import pymysql
import threading
from dbutils.persistent_db import PersistentDB
from settings import cfg


pool = PersistentDB(pymysql, 2,
                    host=cfg.get('db', 'host'),
                    user=cfg.get('db', 'user'),
                    passwd=cfg.get('db', 'pswd'),
                    db=cfg.get('db', 'name'),
                    port=int(cfg.get('db', 'port'))
                    )

class connecting(threading.local):

    def __init__(self):
        # threading.local.__init__(self)
        super(connecting, self).__init__()
        self.engine = pool

    def __enter__(self):
        self.conn = self.engine.connection()
        self.cursor = self.engine.connection().cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

class DbProxy(object):
    @classmethod
    def _raw(cls, sql, *args, **kwargs):
        with connecting() as cursor:
            cursor.execute(sql, *args)
            return cursor.fetchall()

    @classmethod
    def test(cls, dt):
        result = cls._raw("select device_sn,create_time from t_device where create_time > '2021-06-01'", ())
        return result

    # 获取所有工程信息
    @classmethod
    def get_all_projects(cls):
        result = cls._raw("select id,name,province,city,district,position,owner_company from n_project")
        return result

    # 获取一体化设备列表
    @classmethod
    def get_unity_list(cls):
        result = cls._raw("select distinct(device_sn) from t_unify_data_raw")
        return result

    # 查询一体化数据
    @classmethod
    def get_unity_data_raw(cls, device_sn, start, end):
        result = cls._raw("select meas_type,meas_time,value from t_unify_data_raw where device_sn=%s and meas_time>%s and meas_time<%s",    #  order by meas_time
                          (device_sn, start, end,))
        return result

    # 获取外键设备ID
    @classmethod
    def get_device_id(cls, device_sn):
        result = cls._raw("select id from t_device where device_sn=%s",
                          (device_sn,))
        return result

    # 获取一体化休息时间
    @classmethod
    def get_device_rest_time(cls, device_id):
        result = cls._raw("select rest_time from t_unify_param where device_id=%s",
                          (device_id,))
        return result

    # 得到【项目】详情
    @classmethod
    def get_project_info(cls, id):
        project_info = cls._raw("select "
                                  "name,abstract,monitor_results,map_loc "
                                  "from n_project "
                                  "where "
                                  "id=%s",
                                  (id,))
        return project_info

    # 得到【子项目】详情
    @classmethod
    def get_sub_project_info(cls, id):
        sub_project_info = cls._raw("select "
                                    "name,engine_cate,paper_time,detect_cate,data_analysis,analysis_by_synthesis,"
                                    "sub_abstract,monitor_object,build_company,construct_company,supervise_company,detect_company,"
                                    "general_layout "
                                    "from n_sub_project "
                                    "where "
                                    "id=%s",
                                  (id,))
        return sub_project_info

    # 得到【监测因素】详情
    @classmethod
    def get_factor_info(cls, id):
        factor_info = cls._raw("select "
                                  "name,type,monitor_result,sensor_layout,monitor_conclusion "
                                  "from n_monitor_factor "
                                  "where id=%s",
                                  (id,))
        return factor_info

    # 得到【监测点位】详情
    @classmethod
    def get_point_info(cls, id):
        point_info = cls._raw("select "
                              "name,device_sn,cumulative_change,average_rate_day,average_rate_7days,trend,"
                              "id,section_layout,section_monitor_conclusion,related_info "
                              "from n_monitor_point "
                              "where "
                              "id=%s",
                              (id,))
        return point_info

    # 得到【项目】下所有【子项目】
    @classmethod
    def get_sub_projects(cls, project_id):
        '''
        '''
        sub_projects_id = cls._raw("select id,name from n_sub_project where project_id=%s",
                                   (project_id,))
        return sub_projects_id

    # 得到【子项目】下所有【监测因素】
    @classmethod
    def get_monitor_factors(cls, sub_project_id):
        monitor_factors_id = cls._raw("select id from n_monitor_factor where sub_project_id=%s",
                                      (sub_project_id,))
        return monitor_factors_id

    # 得到【监测因素】下所有【监测点位】
    @classmethod
    def get_monitor_points(cls, monitor_factor_id):
        monitor_points_id = cls._raw("select id from n_monitor_point where monitor_factor_id=%s",
                                     (monitor_factor_id,))
        return monitor_points_id

    # 查询outline数据
    @classmethod
    def get_outline_data(cls, device_sn, start, end):
        result = cls._raw("select meas_time,result from t_outline_result where device_sn=%s and meas_time>%s and meas_time<%s order by meas_time",
                          (device_sn, start, end,))
        return result


    # @classmethod
    # def get_outline_data_raw(cls, device_sn, start, end):
    #     result = cls._raw("select meas_time,angle,range from t_collect_raw where device_sn=%s and meas_time>%s and meas_time<%s order by meas_time",
    #                       (device_sn, start, end,))
    #     return result


if __name__ == '__main__':
    pass











