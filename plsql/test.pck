create or replace package test is

  -- Author  : ��������_�
  -- Created : 22.06.2021 16:13:21
  -- Purpose : ��������� ������������
  
  -- Public type declarations
  procedure get_theme(iid_person in number, otheme_name out nvarchar2, ostatus_testing out nvarchar2);
  
  function navigate_question(iid_person in number, icommand in number) return number;
  procedure set_answer(iid_person in number, iorder_num_answer in number);

  procedure finish(iid_person in number);
  function finish_info(iid_person in number) return nvarchar2;
  function have_test(iid_person in number) return number;
  
  
  function get_question(iid_person in number) return nvarchar2;
  function get_result(iid_registration in number) return sys_refcursor;
  procedure get_personal_info( iid_person in number, oid_reg out number, 
                             oiin out varchar2, otime_beg out date,
                             otime_end out date, ofio out nvarchar2 );

  procedure get_personal_info( iid_registration in number, 
                             oiin out varchar2, otime_beg out date,
                             otime_end out date, ofio out nvarchar2 );

end test;
/
create or replace package body test is


  procedure log(imess in nvarchar2)
  is
  PRAGMA AUTONOMOUS_TRANSACTION;
  begin
    insert into protocol(event_date, message) values(systimestamp, imess);
    commit;
  end;

  procedure get_theme(iid_person in number, otheme_name out nvarchar2, ostatus_testing out nvarchar2)
  is
  begin
    select tft.theme_number || '. '|| th.descr, t.status_testing
    into otheme_name, ostatus_testing
    from themes th, themes_for_testing tft, 
         testing t
    where th.id_theme=t.id_current_theme
    and t.id_registration=tft.id_registration
    and t.id_current_theme=tft.id_theme
    and t.status='Active'
    and t.id_person=iid_person;
  end;
  
  procedure set_answer(iid_person in number, iorder_num_answer in number)
  is
    v_id_question_for_testing questions_for_testing.id_question_for_testing%type;
    v_id_registration testing.id_registration%type;
    v_id_answer  pls_integer;
  begin
    select t.id_registration, id_question_for_testing
    into   v_id_registration, v_id_question_for_testing    
    from questions_for_testing qft, testing t
    where qft.id_registration=t.id_registration
    and   qft.id_theme=t.id_current_theme
    and   qft.order_num_question=t.current_num_question
    and   t.id_person=iid_person
    and   t.status='Active';
    
    select id_answer
    into v_id_answer
    from answers_in_testing ait
    where ait.order_num_answer=iorder_num_answer
    and   ait.id_question_for_testing = v_id_question_for_testing;
     
    update questions_for_testing qft
    set    qft.id_answer=v_id_answer
    where qft.id_question_for_testing=v_id_question_for_testing;

    insert into protocol(event_date,message) 
           values(SYSTIMESTAMP, '��������� ���������, id_person: '||iid_person||', num_answer: '||iorder_num_answer||', question_for_testing: '||v_id_question_for_testing);
    commit;
    exception when others then 
      log('--- ERROR SET_ANSWER. id_person: '||iid_person||', iorder_num_answer: '||iorder_num_answer||
               ', id_registration: '||v_id_registration||
               ', id_question_for_testing: '||v_id_question_for_testing||
               ', v_id_answer: '||v_id_answer||' : '||sqlerrm);
      raise_application_error(-20000, sqlerrm);
  end;
  
  function next_theme(icommand in number, iid_registration in pls_integer, itheme_number in pls_integer) return pls_integer
  is
    row_tft         themes_for_testing%rowtype;
  begin
    if icommand=2 and itheme_number>1 then
      begin
        select tft.* into row_tft
        from themes_for_testing tft 
        where tft.id_registration=iid_registration
        and   tft.theme_number=itheme_number-1;

        update testing t 
        set    t.id_current_theme=row_tft.id_theme,
               t.current_num_question=row_tft.count_question
        where t.id_registration=row_tft.id_registration;
        
        exception when no_data_found then return -50;
      end;
    end if;
    if icommand=12 then
      begin
        select tft.* into row_tft
        from themes_for_testing tft 
        where tft.id_registration=iid_registration
        and   tft.theme_number=itheme_number+1;

        update testing t 
        set    t.id_current_theme=row_tft.id_theme,
               t.current_num_question=1
        where t.id_registration=row_tft.id_registration;

        exception when no_data_found then return -100;
      end;
    end if;
--    log('NEXT_THEME. ROW_TFT. id_person: '||iid_person||' : '||icommand||', v_theme_number: '||v_theme_number);  
    commit;
    return 0;
  end;
  
  procedure navigate_finish(iid_registration in pls_integer)
  is
  begin
       update testing t
       set    t.last_time_access=systimestamp,
              t.status_testing='�������� ���������'
       where  t.id_registration=iid_registration;
       commit;
  end;
  
  function navigate_question(iid_person in number, icommand in number)
    return number
  is
   v_status_testing  testing.status_testing%type;
   v_count_question pls_integer;
   v_cur_num_question pls_integer;
   v_remain_time      pls_integer;
   v_id_registration  pls_integer;
   v_theme_number     pls_integer;
   v_id_theme         pls_integer;
  begin
--    insert into protocol(event_date,message) values(SYSTIMESTAMP, '�������� ������� '|| icommand|| ', id_person: '||iid_person);
--    commit;
    begin
    /*������� ����� ���������� �������� � ���������� ����� ��� �����������*/
     select tft.id_registration, tft.theme_number, tft.count_question, t.current_num_question, t.status_testing,
            ( extract(second from t.beg_time_testing - systimestamp) + 
              extract(minute from t.beg_time_testing - systimestamp)*60 + 
              extract(hour from t.beg_time_testing - systimestamp)*3600 + 
              t.period_for_testing 
            )
            into v_id_registration, v_theme_number, v_count_question, v_cur_num_question, v_status_testing, v_remain_time
     from themes_for_testing tft, testing t
     where tft.id_registration=t.id_registration
     and   tft.id_theme=t.id_current_theme
     and   t.status='Active'       
     and   t.id_person=iid_person;
    exception when no_data_found then
      log('Navigate_question. Error! Absend DATA for testing!');
      return 0;
    end;
    log('1. navigate_question. id_person: '||iid_person||' : '||icommand||' id_registration: '||v_id_registration||
            ', theme_number: '||v_theme_number||', num_question: '||v_cur_num_question||', time remain: '||v_remain_time);

    if v_status_testing='Completed' then
       return 0;
    end if;
    /* ���� � ������, � ������� ������������� ������� */
    if icommand=5 or v_status_testing='��������' then
       begin
--          log('Commmand=5. ����');
          select order_num_question, id_theme
          into v_cur_num_question, v_theme_number
          from (
              select q.order_num_question, tft.id_theme
              from testing t, themes_for_testing tft, 
                   questions_for_testing q
              where t.id_registration=tft.id_registration
              and   t.id_registration=q.id_registration
              and   q.id_theme=tft.id_theme
              and   t.id_person=iid_person
              and t.status='Active'
              and coalesce(q.id_answer,0)=0
              order by theme_number, order_num_question
          )
          where rownum=1;

--          log('Commmand=5. ���������. v_cur_num_question: '||v_cur_num_question||', id_theme: '||v_theme_number||', v_id_registration: '||v_id_registration);
          if v_status_testing!='��������'
          then
              update testing t 
              set t.status_testing='��������'
              where t.id_registration=v_id_registration;
          end if;
          
       exception when no_data_found then
          if v_status_testing='��������' 
          then
--              log('Commmand=5. Exception Finish.'|| v_id_registration);
              navigate_finish(v_id_registration);
              return -100; --������ WEB-�� ��� ���� ������������
          else
              select order_num_question, id_theme
              into v_cur_num_question, v_theme_number
              from (
                  select q.order_num_question, tft.id_theme
                  from testing t, themes_for_testing tft, 
                       questions_for_testing q
                  where t.id_registration=tft.id_registration
                  and   t.id_registration=q.id_registration
                  and   q.id_theme=tft.id_theme
                  and   t.id_person=iid_person
                  and t.status='Active'
                  order by theme_number, order_num_question
              )
              where rownum=1;
          end if;

--          log('Commmand=5. Exception Select. v_cur_num_question: '||v_cur_num_question||', id_theme: '||v_theme_number||', v_id_registration: '||v_id_registration);
          update testing t 
          set t.status_testing='������ ��������'
          where t.id_registration=v_id_registration;
       end;
        
--       log('Commmand=5. Update. v_cur_num_question: '||v_cur_num_question||', id_theme: '||v_theme_number||', v_id_registration: '||v_id_registration);
       update testing t
       set    t.current_num_question=v_cur_num_question,
              t.id_current_theme=v_theme_number,
              t.last_time_access=systimestamp
       where  t.id_registration=v_id_registration;
       commit;
       return v_remain_time;
    end if;
    /* ���� � ������ ������������, � ������� ������� */
    if icommand=0 then
       select id_theme 
       into v_id_theme
       from (
           select tft.id_theme
           from themes_for_testing tft
           where tft.id_registration=v_id_registration
           order by tft.theme_number
       )
       where rownum=1;
       
       update testing t
       set    t.current_num_question=1,
              t.id_current_theme=v_id_theme,
              t.last_time_access=systimestamp
       where  t.id_registration=v_id_registration;
    end if;
    /* ���� � ������ �������, � ������� ������� */
    if icommand=1 then
       update testing t
       set    t.current_num_question=1,
              t.last_time_access=systimestamp
       where  t.id_registration=v_id_registration;
    end if;
    /* ���� � ����� �������*/
    if icommand=11 then
       update testing t
       set    t.current_num_question=v_count_question,
              t.last_time_access=systimestamp
       where  t.id_registration=v_id_registration;
    end if;
    /* */
    /* ���� � ������ ������������, � ������� ������� */
    if icommand=10 then
       select id_theme 
       into v_id_theme
       from (
           select tft.id_theme
           from themes_for_testing tft
           where tft.id_registration=v_id_registration
           order by tft.theme_number desc
       )
       where rownum=1;
       
       update testing t
       set    t.current_num_question=v_count_question,
              t.id_current_theme=v_id_theme,
              t.last_time_access=systimestamp
       where  t.id_registration=v_id_registration;
    end if;
    /* ��������� ������ */
    if icommand=12 then
      
       if v_cur_num_question=v_count_question then
          if next_theme(icommand, v_id_registration, v_theme_number)=-100 then
              log('2. ABSENT NEXT THEME. navigate_question. id_person: '||iid_person||' : '||icommand||' id_registration: '||v_id_registration||
                      ', theme_number: '||v_theme_number||', num_question: '||v_cur_num_question||', time remain: '||v_remain_time);
            return -100;
          end if;
       else 
          update testing t
          set    t.current_num_question=current_num_question+1,
                t.last_time_access=systimestamp
          where  t.id_registration=v_id_registration;
       end if;
    end if;
    /* ���������� ������ */
    if icommand=2 then
       if v_cur_num_question=1 then
         if next_theme(icommand, v_id_registration, v_theme_number)=-50 then
           return -50;
         end if;
       else
          update testing t
          set    t.current_num_question=current_num_question-1,
                 t.last_time_access=systimestamp
          where  t.id_registration=v_id_registration;
       end if;
    end if;

    commit;
    return v_remain_time;
  end;

  function finish_info(iid_person in number) return nvarchar2
  is
    v_unanswered       pls_integer;
  begin
      select count(q.id_question) 
      into v_unanswered
      from testing t, themes_for_testing tft, 
           questions_for_testing q
      where t.id_registration=tft.id_registration
      and   t.id_registration=q.id_registration
      and   q.id_theme=tft.id_theme
      and   t.id_person=iid_person
      and t.status='Active'
      and coalesce(q.id_answer,0)=0;
                        
      if v_unanswered>0 then
         insert into protocol(event_date,message) 
                values(SYSTIMESTAMP, '������� ������������ �������. id_person: '|| iid_person ||', � ����������: ' ||v_unanswered);
         commit;
         return to_char(v_unanswered);
      end if;
      return '';
  end;

  procedure finish(iid_person in number)
  is
    rec_testing        testing%rowtype;
  begin
    select * into rec_testing from testing t where t.status='Active' and t.id_person=iid_person;
    
    if rec_testing.status_testing!='Completed'
    then
        update testing t
        set   t.status_testing='Completed',
              t.end_time_testing=systimestamp
        where t.id_registration=rec_testing.id_registration;
        commit;
    end if;
  end;


  function have_test(iid_person in number) return number
  is
    v_cnt        pls_integer;
  begin
    select t.period_for_testing into v_cnt
    from testing t
    where t.status='Active'
    and   t.id_person=iid_person;
    
    update testing t
    set t.beg_time_testing=systimestamp,
        t.last_time_access=systimestamp,
        t.status_testing='���� ������������'
    where t.status='Active'
    and   t.id_person=iid_person;
    commit;
    return v_cnt;
    exception when no_data_found then return '';
  end;

  function get_question(iid_person in number) return nvarchar2
  is
  omess nvarchar2(128);
  begin
    select q.question
    into omess
    from questions q, 
         questions_for_testing qft,
         testing t
    where qft.id_question=q.id_question
    and qft.id_registration=t.id_registration 
    and q.id_theme=t.id_current_theme
    and qft.order_num_question=t.current_num_question
    and t.status='Active'
    and t.id_person=iid_person;
   
    return omess;
  end;
  
  procedure get_personal_info( iid_person in number, oid_reg out number, 
                             oiin out varchar2, otime_beg out date,
                             otime_end out date, ofio out nvarchar2 )
  is                             
  begin
    select t.id_registration, 
           p.iin, beg_time_testing, end_time_testing, fio
    into oid_reg, oiin, otime_beg, otime_end, ofio
    from persons p, testing t
    where p.id_person=iid_person
    and   p.id_person=t.id_person
    and   t.status='Active';
  end;

  procedure get_personal_info( iid_registration in number, 
                             oiin out varchar2, otime_beg out date,
                             otime_end out date, ofio out nvarchar2 )
  is                             
  begin
    select p.iin, beg_time_testing, end_time_testing, fio
    into oiin, otime_beg, otime_end, ofio
    from persons p, testing t
    where t.id_registration=iid_registration
    and   p.id_person=t.id_person
    and   t.status='Active';
    exception when no_data_found 
      then begin
        oiin:='';
        otime_beg:='';
        otime_end:='';
        ofio:='';
      end;
  end;

                                 
  function get_result(iid_registration in number) return sys_refcursor
  is 
    rf_cur sys_refcursor;
  begin
      open rf_cur for
          select theme_number, descr, count_question, count_success,
                 sum(true_result) true_score,
                 sum(false_result) false_score
          from(       
          select th.id_theme, theme_number, th.descr, tft.count_question, tft.count_success,
                 case when correctly='Y' then 1 else 0 end true_result,
                 case when correctly!='Y' then 1 else 0 end false_result
          from questions_for_testing qft, answers a,
               themes_for_testing tft, themes th
          where qft.id_registration=tft.id_registration
          and qft.id_theme=th.id_theme
          and a.id_answer(+)=qft.id_answer
          and tft.id_registration=iid_registration
          and   tft.id_theme=th.id_theme 
          )
          group by theme_number, count_question, count_success, descr;
      return rf_cur;
  end;

begin
  null;
end test;
/
