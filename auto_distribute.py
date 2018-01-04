from crm import models


class AutoDistribute(object):
    users = None # [1,2,1,2,3,1,...]
    iter_users = None # iter([1,2,1,2,3,1,...])
    reset_status = False
    roll_back_list=[]#放置出错时，伪造迭代器需要回滚的id

    @classmethod
    def fetch_users(cls):
        sales_list = models.SaleRank.objects.all().order_by('-weight')
        count=0
        v=[]
        while True:
            flag = False
            for i in sales_list:
                if count < i.num:
                    v.append(i.id)
                    flag=True
                count += 1
            if not flag:
                break
        print(v)
        cls.users=v
        # v = [短期, 番禺, 富贵, 秦晓, 短期, 番禺, 富贵, 秦晓, 番禺, 富贵, 秦晓, 秦晓, 秦晓, 秦晓, 秦晓, 秦晓, 秦晓...]


    @classmethod
    def get_sale_id(cls):
        if cls.roll_back_list:
            #如果回滚列表有值，就说明需要回滚
            return cls.roll_back_list.pop()
        if not cls.users:
            #事务没问题，不需要回滚，得到v
            cls.fetch_users()
        if not cls.users:
            # v是空的，说明没有空闲销售
            return None
        if not cls.iter_users:
            #迭代器
            cls.iter_users = iter(cls.users)
        try:
            #实现迭代
            user_id = next(cls.iter_users)
        except StopIteration as e:
            if cls.reset_status:
                #迭代完了，用递归实现循坏
                cls.fetch_users()
                cls.reset_status = False
            cls.iter_users = iter(cls.users)
            user_id = cls.get_sale_id()
        return user_id

    @classmethod
    def reset(cls):
        cls.reset_status = True

    @classmethod
    def rollback(cls, nid):
        #事务出错，需要回滚id
        cls.roll_back_list.insert(0, nid)