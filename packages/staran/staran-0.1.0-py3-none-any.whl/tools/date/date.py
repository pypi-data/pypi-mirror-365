# 定义类
class Date:
    # 类变量：C扩展可用性检查
    _c_extension_checked = False
    _has_c_extension = False
    
    @classmethod
    def _check_c_extension(cls):
        """检查C扩展是否可用（只检查一次）"""
        if not cls._c_extension_checked:
            try:
                from . import platform_utils
                cls._has_c_extension = platform_utils.has_c_extension()
                cls._c_extension_checked = True
            except (ImportError, AttributeError):
                cls._has_c_extension = False
                cls._c_extension_checked = True
        return cls._has_c_extension
    
    @classmethod
    def has_c_extension(cls):
        """检查是否有C扩展可用"""
        return cls._check_c_extension()
    
    @classmethod
    def get_platform_info(cls):
        """获取平台信息"""
        try:
            from . import platform_utils
            return platform_utils.get_platform_info()
        except (ImportError, AttributeError):
            import platform
            return {
                'system': platform.system(),
                'machine': platform.machine(),
                'python_version': platform.python_version(),
                'has_c_extension': False,
                'implementation': 'Python fallback'
            }
    
    def __init__(self, *args, **kwargs):
        # 如果传入一个参数且是字符串，则交给方法 parse_date
        if len(args) == 1 and isinstance(args[0], str):
            self._str_date(args[0])
        # 如果传入位置参数（2个或3个）
        elif len(args) in [2, 3]:
            self._init_from_args(args)
        # 如果使用关键字参数
        elif kwargs:
            self._init_from_kwargs(kwargs)
        # 如果没有参数，使用当天日期
        elif len(args) == 0:
            self._init_from_today()
        else:
            raise ValueError("Invalid arguments provided to Date class")
        
        # 对所有非字符串初始化的情况进行验证
        # 如果不是通过parse_date设置的（即不是从字符串解析的），则需要验证
        if not (len(args) == 1 and isinstance(args[0], str)):
            self._validate_date_values()

    def _init_from_args(self, args):
        """从位置参数初始化日期"""
        if len(args) == 2:
            self.year, self.month = args
            self.day = 1
        elif len(args) == 3:
            self.year, self.month, self.day = args

    def _init_from_kwargs(self, kwargs):
        """从关键字参数初始化日期"""
        # 获取当天日期作为默认值
        try:
            from . import platform_utils
            default_year, default_month, default_day = platform_utils.get_today()
        except (ImportError, AttributeError):
            # 回退到datetime实现
            import datetime
            today = datetime.date.today()
            default_year, default_month, default_day = today.year, today.month, today.day
        
        self.year = kwargs.get('year', default_year)
        self.month = kwargs.get('month', default_month)
        self.day = kwargs.get('day', default_day)

    def _init_from_today(self):
        """使用当天日期初始化"""
        try:
            from . import platform_utils
            self.year, self.month, self.day = platform_utils.get_today()
        except (ImportError, AttributeError):
            # 回退到datetime实现
            import datetime
            today = datetime.date.today()
            self.year, self.month, self.day = today.year, today.month, today.day

    def _validate_year(self, year):
        """验证年份是否有效"""
        if not isinstance(year, int):
            raise ValueError(f"Year must be an integer, got {type(year).__name__}")
        if year < 1:
            raise ValueError(f"Year must be positive, got {year}")
        return year

    def _validate_month(self, month):
        """验证月份是否有效"""
        if not isinstance(month, int):
            raise ValueError(f"Month must be an integer, got {type(month).__name__}")
        if not (1 <= month <= 12):
            raise ValueError(f"Month must be between 1 and 12, got {month}")
        return month

    def _validate_day(self, day):
        """验证日期是否有效"""
        if not isinstance(day, int):
            raise ValueError(f"Day must be an integer, got {type(day).__name__}")
        if not (1 <= day <= 31):
            raise ValueError(f"Day must be between 1 and 31, got {day}")
        return day

    def _validate_date_values(self):
        """验证年、月、日的组合是否合理"""
        self.year = self._validate_year(self.year)
        self.month = self._validate_month(self.month)
        self.day = self._validate_day(self.day)
        
        # 验证日期组合
        self._validate_date_combination()

    def _is_leap_year(self, year):
        """检查是否为闰年"""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    # 定义方法，删除原有字符串的 - / . 字符
    # 删除后如果为6位，则为 YYYYMM 格式
    # 如果为8位，则为 YYYYMMDD 格式
    def _str_date(self, date_str):
        if not date_str or not isinstance(date_str, str):
            raise ValueError("Date string cannot be empty or None")
        
        # 清理字符串，移除分隔符
        cleaned_str = date_str.replace("-", "").replace("/", "").replace(".", "")
        
        # 验证长度和内容
        if len(cleaned_str) not in [6, 8]:
            raise ValueError(f"Date string must be 6 (YYYYMM) or 8 (YYYYMMDD) digits after removing separators, got {len(cleaned_str)}")
        
        if not cleaned_str.isdigit():
            raise ValueError("Date string must contain only digits and separators")
        
        try:
            year = int(cleaned_str[:4])
            month = int(cleaned_str[4:6])
            day = int(cleaned_str[6:]) if len(cleaned_str) == 8 else 1
            
            # 使用验证方法
            self.year = self._validate_year(year)
            self.month = self._validate_month(month)
            self.day = self._validate_day(day)
            
            # 验证日期组合的合理性
            self._validate_date_combination()
                
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("Date string contains invalid characters")
            raise

    def _validate_date_combination(self):
        """验证年、月、日组合是否合理（不重复验证单个值）"""
        # 进一步验证日期是否在该月份的有效范围内
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # 检查闰年
        if self._is_leap_year(self.year):
            days_in_month[1] = 29
            
        if self.day > days_in_month[self.month - 1]:
            raise ValueError(f"Day {self.day} is invalid for {self.year}-{self.month:02d}")

    def past_month(self, months=1):
        """
        获取过去的月份
        
        Args:
            months (int): 往前推的月份数，默认为1
            
        Returns:
            Date: 新的Date对象，表示过去指定月份的日期
        """
        if not isinstance(months, int) or months < 0:
            raise ValueError("Months must be a non-negative integer")
        
        # 计算新的年份和月份
        new_year = self.year
        new_month = self.month - months
        
        # 处理月份跨年的情况
        while new_month <= 0:
            new_month += 12
            new_year -= 1
            
        # 处理日期可能超出目标月份天数的情况
        new_day = self._adjust_day_for_month(new_year, new_month, self.day)
        
        return Date(new_year, new_month, new_day)

    def future_month(self, months=1):
        """
        获取未来的月份
        
        Args:
            months (int): 往后推的月份数，默认为1
            
        Returns:
            Date: 新的Date对象，表示未来指定月份的日期
        """
        if not isinstance(months, int) or months < 0:
            raise ValueError("Months must be a non-negative integer")
        
        # 计算新的年份和月份
        new_year = self.year
        new_month = self.month + months
        
        # 处理月份跨年的情况
        while new_month > 12:
            new_month -= 12
            new_year += 1
            
        # 处理日期可能超出目标月份天数的情况
        new_day = self._adjust_day_for_month(new_year, new_month, self.day)
        
        return Date(new_year, new_month, new_day)

    def _adjust_day_for_month(self, year, month, day):
        """
        调整日期以适应目标月份的天数
        
        Args:
            year (int): 目标年份
            month (int): 目标月份
            day (int): 原始日期
            
        Returns:
            int: 调整后的日期
        """
        # 获取目标月份的天数
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # 检查闰年
        if self._is_leap_year(year):
            days_in_month[1] = 29
            
        max_day = days_in_month[month - 1]
        
        # 如果原日期超过目标月份的最大天数，则使用目标月份的最后一天
        return min(day, max_day)

    def past_year(self, years=1):
        """
        获取过去的年份
        
        Args:
            years (int): 往前推的年份数，默认为1
            
        Returns:
            Date: 新的Date对象，表示过去指定年份的日期
        """
        if not isinstance(years, int) or years < 0:
            raise ValueError("Years must be a non-negative integer")
        
        new_year = self.year - years
        new_month = self.month
        new_day = self.day
        
        # 处理2月29日在非闰年的情况
        if new_month == 2 and new_day == 29 and not self._is_leap_year(new_year):
            new_day = 28
            
        return Date(new_year, new_month, new_day)

    def future_year(self, years=1):
        """
        获取未来的年份
        
        Args:
            years (int): 往后推的年份数，默认为1
            
        Returns:
            Date: 新的Date对象，表示未来指定年份的日期
        """
        if not isinstance(years, int) or years < 0:
            raise ValueError("Years must be a non-negative integer")
        
        new_year = self.year + years
        new_month = self.month
        new_day = self.day
        
        # 处理2月29日在非闰年的情况
        if new_month == 2 and new_day == 29 and not self._is_leap_year(new_year):
            new_day = 28
            
        return Date(new_year, new_month, new_day)

    def past_day(self, days=1):
        """
        获取过去的天数
        
        Args:
            days (int): 往前推的天数，默认为1
            
        Returns:
            Date: 新的Date对象，表示过去指定天数的日期
        """
        if not isinstance(days, int) or days < 0:
            raise ValueError("Days must be a non-negative integer")
        
        # 使用纯算法计算
        new_year = self.year
        new_month = self.month
        new_day = self.day - days
        
        # 处理日期减法跨月的情况
        while new_day <= 0:
            new_month -= 1
            if new_month <= 0:
                new_month = 12
                new_year -= 1
            
            # 获取新月份的天数
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if self._is_leap_year(new_year):
                days_in_month[1] = 29
            
            new_day += days_in_month[new_month - 1]
        
        return Date(new_year, new_month, new_day)

    def future_day(self, days=1):
        """
        获取未来的天数
        
        Args:
            days (int): 往后推的天数，默认为1
            
        Returns:
            Date: 新的Date对象，表示未来指定天数的日期
        """
        if not isinstance(days, int) or days < 0:
            raise ValueError("Days must be a non-negative integer")
        
        # 使用纯算法计算
        new_year = self.year
        new_month = self.month
        new_day = self.day + days
        
        # 处理日期加法跨月的情况
        while True:
            # 获取当前月份的天数
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if self._is_leap_year(new_year):
                days_in_month[1] = 29
            
            max_day = days_in_month[new_month - 1]
            
            if new_day <= max_day:
                break
                
            new_day -= max_day
            new_month += 1
            
            if new_month > 12:
                new_month = 1
                new_year += 1
        
        return Date(new_year, new_month, new_day)

    def past_week(self, weeks=1):
        """
        获取过去的周数
        
        Args:
            weeks (int): 往前推的周数，默认为1
            
        Returns:
            Date: 新的Date对象，表示过去指定周数的日期
        """
        if not isinstance(weeks, int) or weeks < 0:
            raise ValueError("Weeks must be a non-negative integer")
        
        return self.past_day(weeks * 7)

    def future_week(self, weeks=1):
        """
        获取未来的周数
        
        Args:
            weeks (int): 往后推的周数，默认为1
            
        Returns:
            Date: 新的Date对象，表示未来指定周数的日期
        """
        if not isinstance(weeks, int) or weeks < 0:
            raise ValueError("Weeks must be a non-negative integer")
        
        return self.future_day(weeks * 7)

    def add_years(self, years):
        """
        智能年份操作：根据正负值自动判断增加或减少年份
        
        Args:
            years (int): 年份数，正数表示未来，负数表示过去，0表示不变
            
        Returns:
            Date: 新的Date对象
        """
        if not isinstance(years, int):
            raise ValueError("Years must be an integer")
        
        if years == 0:
            return Date(self.year, self.month, self.day)
        elif years > 0:
            return self.future_year(years)
        else:
            return self.past_year(abs(years))

    def add_months(self, months):
        """
        智能月份操作：根据正负值自动判断增加或减少月份
        
        Args:
            months (int): 月份数，正数表示未来，负数表示过去，0表示不变
            
        Returns:
            Date: 新的Date对象
        """
        if not isinstance(months, int):
            raise ValueError("Months must be an integer")
        
        if months == 0:
            return Date(self.year, self.month, self.day)
        elif months > 0:
            return self.future_month(months)
        else:
            return self.past_month(abs(months))

    def add_weeks(self, weeks):
        """
        智能周数操作：根据正负值自动判断增加或减少周数
        
        Args:
            weeks (int): 周数，正数表示未来，负数表示过去，0表示不变
            
        Returns:
            Date: 新的Date对象
        """
        if not isinstance(weeks, int):
            raise ValueError("Weeks must be an integer")
        
        if weeks == 0:
            return Date(self.year, self.month, self.day)
        elif weeks > 0:
            return self.future_week(weeks)
        else:
            return self.past_week(abs(weeks))

    def add_days(self, days):
        """
        智能天数操作：根据正负值自动判断增加或减少天数
        
        Args:
            days (int): 天数，正数表示未来，负数表示过去，0表示不变
            
        Returns:
            Date: 新的Date对象
        """
        if not isinstance(days, int):
            raise ValueError("Days must be an integer")
        
        if days == 0:
            return Date(self.year, self.month, self.day)
        elif days > 0:
            return self.future_day(days)
        else:
            return self.past_day(abs(days))

    def delta(self, years=0, months=0, weeks=0, days=0):
        """
        组合时间操作：同时处理年、月、周、天的增减
        
        Args:
            years (int): 年份增减数，默认为0
            months (int): 月份增减数，默认为0
            weeks (int): 周数增减数，默认为0
            days (int): 天数增减数，默认为0
            
        Returns:
            Date: 新的Date对象
        """
        # 按顺序应用操作：年 → 月 → 周 → 天
        result = self.add_years(years)
        result = result.add_months(months)
        result = result.add_weeks(weeks)
        result = result.add_days(days)
        
        return result

    # ==================== 日期比较方法 ====================
    
    def days_between(self, other_date):
        """
        计算两个日期之间的天数差
        
        Args:
            other_date (Date): 另一个日期对象
            
        Returns:
            int: 天数差，正数表示other_date在未来，负数表示在过去
        """
        if not isinstance(other_date, Date):
            raise ValueError("other_date must be a Date object")
        
        # 将日期转换为从公元1年1月1日开始的天数
        def date_to_days(date):
            total_days = 0
            
            # 加上年份的天数
            for year in range(1, date.year):
                if self._is_leap_year(year):
                    total_days += 366
                else:
                    total_days += 365
            
            # 加上月份的天数
            days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if self._is_leap_year(date.year):
                days_in_month[1] = 29
            
            for month in range(1, date.month):
                total_days += days_in_month[month - 1]
            
            # 加上天数
            total_days += date.day
            
            return total_days
        
        days1 = date_to_days(self)
        days2 = date_to_days(other_date)
        
        return days2 - days1

    def is_before(self, other_date):
        """判断是否在另一个日期之前"""
        return self.days_between(other_date) > 0

    def is_after(self, other_date):
        """判断是否在另一个日期之后"""
        return self.days_between(other_date) < 0

    def is_same(self, other_date):
        """判断是否是同一天"""
        return self.days_between(other_date) == 0

    # ==================== 日期信息查询方法 ====================
    
    def weekday(self):
        """
        获取星期几
        
        Returns:
            int: 0=周一, 1=周二, ..., 6=周日
        """
        # 使用 Zeller 公式计算星期几
        # 将1月和2月看作上一年的13月和14月
        if self.month < 3:
            month = self.month + 12
            year = self.year - 1
        else:
            month = self.month
            year = self.year
        
        # Zeller公式
        h = (self.day + (13 * (month + 1)) // 5 + year + year // 4 - year // 100 + year // 400) % 7
        
        # 转换为周一=0的格式 (Zeller公式中: 0=周六, 1=周日, 2=周一...)
        return (h + 5) % 7

    def weekday_name(self, lang='zh'):
        """
        获取星期几的名称
        
        Args:
            lang (str): 语言，'zh'=中文, 'en'=英文
            
        Returns:
            str: 星期几的名称
        """
        weekday_names = {
            'zh': ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        }
        return weekday_names.get(lang, weekday_names['zh'])[self.weekday()]

    def month_name(self, lang='zh'):
        """
        获取月份名称
        
        Args:
            lang (str): 语言，'zh'=中文, 'en'=英文
            
        Returns:
            str: 月份名称
        """
        month_names = {
            'zh': ['一月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '十一月', '十二月'],
            'en': ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
        }
        return month_names.get(lang, month_names['zh'])[self.month - 1]

    def quarter(self):
        """
        获取季度
        
        Returns:
            int: 季度 (1-4)
        """
        return (self.month - 1) // 3 + 1

    def day_of_year(self):
        """
        获取一年中的第几天
        
        Returns:
            int: 一年中的第几天 (1-366)
        """
        # 每月天数
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        # 检查闰年
        if self._is_leap_year(self.year):
            days_in_month[1] = 29
        
        # 累加前面月份的天数，再加上当前月的天数
        total_days = sum(days_in_month[:self.month - 1]) + self.day
        
        return total_days

    def week_of_year(self):
        """
        获取一年中的第几周
        
        Returns:
            int: 一年中的第几周
        """
        # 计算1月1日是星期几
        jan_1 = Date(self.year, 1, 1)
        jan_1_weekday = jan_1.weekday()
        
        # 计算当前日期是一年中的第几天
        day_of_year = self.day_of_year()
        
        # 计算第一周的天数（1月1日到第一个周日的天数）
        # 如果1月1日是周一(0)，第一周有7天
        # 如果1月1日是周二(1)，第一周有6天，以此类推
        first_week_days = 7 - jan_1_weekday
        
        if day_of_year <= first_week_days:
            return 1
        else:
            # 减去第一周的天数，然后除以7，再加1
            return ((day_of_year - first_week_days - 1) // 7) + 2

    # ==================== 特殊日期判断方法 ====================
    
    def is_weekend(self):
        """判断是否是周末"""
        return self.weekday() >= 5  # 周六(5)或周日(6)

    def is_leap_year_date(self):
        """判断当前日期所在年份是否是闰年"""
        return self._is_leap_year(self.year)

    def is_month_end(self):
        """判断是否是月末"""
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if self._is_leap_year(self.year):
            days_in_month[1] = 29
        return self.day == days_in_month[self.month - 1]

    def is_quarter_end(self):
        """判断是否是季度末"""
        return self.month in [3, 6, 9, 12] and self.is_month_end()

    def is_year_end(self):
        """判断是否是年末"""
        return self.month == 12 and self.day == 31

    # ==================== 日期边界方法 ====================
    
    def start_of_month(self):
        """获取当月第一天"""
        return Date(self.year, self.month, 1)

    def end_of_month(self):
        """获取当月最后一天"""
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if self._is_leap_year(self.year):
            days_in_month[1] = 29
        last_day = days_in_month[self.month - 1]
        return Date(self.year, self.month, last_day)

    def start_of_year(self):
        """获取当年第一天"""
        return Date(self.year, 1, 1)

    def end_of_year(self):
        """获取当年最后一天"""
        return Date(self.year, 12, 31)

    def start_of_quarter(self):
        """获取当季度第一天"""
        quarter_start_months = [1, 4, 7, 10]
        quarter_month = quarter_start_months[self.quarter() - 1]
        return Date(self.year, quarter_month, 1)

    def end_of_quarter(self):
        """获取当季度最后一天"""
        quarter_end_months = [3, 6, 9, 12]
        quarter_month = quarter_end_months[self.quarter() - 1]
        return Date(self.year, quarter_month, 1).end_of_month()

    # ==================== 格式化和转换方法 ====================
    
    def to_dict(self):
        """
        转换为字典格式
        
        Returns:
            dict: 包含年、月、日的字典
        """
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day
        }

    def to_tuple(self):
        """
        转换为元组格式
        
        Returns:
            tuple: (年, 月, 日)
        """
        return (self.year, self.month, self.day)

    def format(self, format_string):
        """
        自定义格式化
        
        Args:
            format_string (str): 格式字符串
                支持: %Y(年), %m(月), %d(日), %M(月名), %W(星期)
                
        Returns:
            str: 格式化后的字符串
        """
        result = format_string
        result = result.replace('%Y', f'{self.year:04d}')
        result = result.replace('%m', f'{self.month:02d}')
        result = result.replace('%d', f'{self.day:02d}')
        result = result.replace('%M', self.month_name())
        result = result.replace('%W', self.weekday_name())
        return result

    def to_iso_string(self):
        """转换为ISO格式字符串"""
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def to_timestamp(self):
        """
        转换为时间戳
        
        Returns:
            float: Unix时间戳
        """
        try:
            from . import platform_utils
            return platform_utils.date_to_timestamp(self.year, self.month, self.day)
        except (ImportError, AttributeError):
            # 回退到datetime实现
            import datetime
            date = datetime.date(self.year, self.month, self.day)
            dt = datetime.datetime.combine(date, datetime.time())
            return dt.timestamp()

    # ==================== 魔术方法支持 ====================
    
    def __eq__(self, other):
        """支持 == 比较"""
        if not isinstance(other, Date):
            return False
        return self.year == other.year and self.month == other.month and self.day == other.day

    def __lt__(self, other):
        """支持 < 比较"""
        if not isinstance(other, Date):
            raise TypeError("Cannot compare Date with non-Date object")
        return self.days_between(other) > 0

    def __le__(self, other):
        """支持 <= 比较"""
        return self < other or self == other

    def __gt__(self, other):
        """支持 > 比较"""
        if not isinstance(other, Date):
            raise TypeError("Cannot compare Date with non-Date object")
        return self.days_between(other) < 0

    def __ge__(self, other):
        """支持 >= 比较"""
        return self > other or self == other

    def __ne__(self, other):
        """支持 != 比较"""
        return not self == other

    def __sub__(self, other):
        """支持日期相减，返回天数差"""
        if isinstance(other, Date):
            return abs(self.days_between(other))
        elif isinstance(other, int):
            return self.add_days(-other)
        else:
            raise TypeError("Cannot subtract non-Date/int from Date")

    def __add__(self, other):
        """支持日期加天数"""
        if isinstance(other, int):
            return self.add_days(other)
        else:
            raise TypeError("Cannot add non-int to Date")

    def __hash__(self):
        """支持作为字典键和集合元素"""
        return hash((self.year, self.month, self.day))

    def __repr__(self):
        """更详细的字符串表示"""
        return f"Date({self.year}, {self.month}, {self.day})"

    # 返回日期的字符串表示，格式为 'YYYY-MM-DD'
    def __str__(self):
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
