% clear; clc; close all;

lim = [0,0];

for iter=3:3
    
    if iter == 1
        Scheme = 'Raj'
    end
    
    if iter == 2
        Scheme = 'Inv'
    end
    
    
    if iter == 3
        Scheme = 'Olf'
    end
    
    if iter == 4
        Scheme = 'ICF'
    end
    
    %Scheme = 'Olf'
    %Scheme = 'CDC'
    
    % Adjacency matrix partially connected
%     adj =[1     0     1     1     0 ;
%         0     1     1     0     1 ;
%         1     1     1     1     1 ;
%         1     0     1     1     0 ;
%         0     1     1     0     1];
    adj =[1     1     0     0     0     0;
          1     1     1     0     0     0;
          0     1     1     1     0     0;
          0     0     1     1     1     0;
          0     0     0     1     1     1;
          0     0     0     0     1     1];
      
    AGENT_NO = size(adj(1,:),2);
    num = AGENT_NO;

    TIME = 60; % Number of time steps to test for
    num_MC = 2000; 
    RMSE3 = zeros(num_MC,TIME);

    MC = 1;
    for MC = 1:num_MC

        x(:,1) = [20 0]'; % Initial position, can be made stochastic

        for i=1:num
            for k=1:TIME
                xhat(:,k,i) = [2+0.1*randn 2+0.1*randn]';
                xbar(:,k,i) = [2+0.1*randn 2+0.1*randn]';
            end
        end

        % Initialisations
        z = zeros(2,TIME,num);
        
        y_ICF = zeros(2,TIME,num);
        K(:,:,:) = zeros(2,2,num);

        %------------------------- Edited-------------------------%

        C = zeros(2,2,num,num);
        C_KCF = zeros(2,2,num);

        P = zeros(2,2,TIME+1,num,num);
        M = zeros(2,2,TIME,num,num);
        F(:,:,:) = zeros(2,2,num);
        Minit = 8.*eye(2);

        % System/sensor matrices
        A = [cos(pi/200) -sin(pi/200); sin(pi/200) cos(pi/200)];
        B = 1.*eye(2);
        H = zeros(2,2,num);
        S_ICF = zeros(2,2,num);
        Q = 1.*eye(2);
        R = zeros(2,2,num);

        for i=1:num
            H(:,:,i) = eye(2);
            R(:,:,i) = 1*eye(2);
            for j=1:num
                
                %P(:,:,1,i,j) = A*Minit*A' + B*Q*B' + abs(rand(size(A*Minit*A')));
                P(:,:,1,i,j) = A*( Minit + 0.01*( rand(size(A)) ))*A' + B*Q*B';
                %P(:,:,1,i,j) = A*Minit*A' + B*Q*B';
            end
        end


        for k=1:TIME   
            
            if (k > 19 && k<40)
                for i=2:6
                    R(:,:,i) = (50000+10*rand)*eye(2);
                end
            else
                for i=2:6
                    R(:,:,i) = (1)*eye(2);
                end
            end
            % System model
            x(:,k+1) = A*x(:,k) + B*mvnrnd ([0;0],Q)';

            % Sensor model
            for i=1:num
                z(:,k,i) = H(:,:,i)*x(:,k) + mvnrnd ([0;0],R(:,:,i))';
            end    
            
            if (Scheme == 'ICF' | Scheme == 'GKF')       
                for i=1:num    
                    S_ICF(:,:,i) = (H(:,:,i)'/(R(:,:,i)))*H(:,:,i);
                    y_ICF(:,k,i) = (H(:,:,i)'/(R(:,:,i)))*z(:,k,i);
                end
            end
            
            % ---------------- Finding Gains ---------------- %
            
            for i=1:num

                % P_ri - P_ii
                sum5 = zeros(2,2);
                for r = 1:num
                    if (r~=i && adj(r,i))
                        sum5 = sum5 + (P(:,:,k,r,i)-P(:,:,k,i,i));
                    end
                end

                %%  

                if all(Scheme == 'Inv')

                    del =  R(:,:,i) + H(:,:,i)*P(:,:,k,i,i)*H(:,:,i)';
                    E = (H(:,:,i)'/(del))*H(:,:,i);

                    % ------------ Solve Ax=b ------------ %

                    n_Neighbors = nnz(adj(i,:))-1;
                    n_Dim = 2;

                    Ao = zeros(n_Neighbors*n_Dim, n_Neighbors*n_Dim);
                    xo = zeros(n_Neighbors*n_Dim, n_Dim)';
                    bo = zeros(n_Neighbors*n_Dim, n_Dim)';


                    n1 = 1;
                    n2 = 1;

                    for r=1:num
                        if (r~=i && adj(r,i))
                            n2 = 1;
                            for s=1:num
                                if (s~=i && adj(s,i))

                                    Ao(n2:n2+n_Dim-1,n1:n1+n_Dim-1) = (P(:,:,k,s,i) - P(:,:,k,i,i))*E*(P(:,:,k,i,r) - P(:,:,k,i,i)) - ( P(:,:,k,s,r) - P(:,:,k,s,i) - P(:,:,k,i,r) + P(:,:,k,i,i) );
                                    n2 = n2 + n_Dim;

                                end

                            end
                            bo(:,n1:n1+n_Dim-1) = (eye(2) - P(:,:,k,i,i)*E)*(P(:,:,k,i,r) - P(:,:,k,i,i));
                            n1 = n1 + n_Dim;
                        end
                    end
                    
                    [Uo, So, Vo] = svd(Ao);
                    
                    lim(1) = min( min(min(So)),lim(1));
                    lim(2) = max( max(max(So)),lim(2));
                    
                    threshold = 1e-2;
                    
                    for ind = 1:n_Neighbors*n_Dim
                        
                        So(ind,ind) = 1/So(ind,ind);
                        
                    end
                    
                    xo(:,:) = bo*Vo*So*Uo';
                    
                    n1 = 1;
                    for r = 1:num
                        if (r~=i && adj(r,i))
                            C(:,:,r,i) = xo(:,n1:n1+n_Dim-1);
                            n1 = n1+n_Dim;
                        end
                    end

                    % K_i
                    sum7 = zeros(2,2);
                    for j=1:num
                        if (j~=i && adj(j,i))
                            sum7 = sum7 + C(:,:,j,i)*(P(:,:,k,j,i) - P(:,:,k,i,i));
                        end
                    end

                    K(:,:,i) = ((P(:,:,k,i,i) + sum7)*H(:,:,i)')/del;
                    
                end 

                %%

                if all(Scheme == 'Raj')

                    L = zeros(2,2);
                    L(:,:) = sum5(:,:);

                    % --- Finding D_ij --- %
                    D_ii = zeros(2,2);
                    for r = 1:num
                        for s = 1:num
                            if (r~=i && s~=i && adj(r,i) && adj(s,i))
                                D_ii = D_ii + (P(:,:,k,r,s)-P(:,:,k,r,i)-P(:,:,k,i,s)+P(:,:,k,i,i));
                            end
                        end
                    end

                    Del = R(:,:,i) + H(:,:,i)*P(:,:,k,i,i)*H(:,:,i)';
                    G = D_ii - L*H(:,:,i)'*inv(Del)*H(:,:,i)*L';

                    if (det(G)~=0)
                       C_KCF(:,:,i) = (P(:,:,k,i,i)*H(:,:,i)'*inv(Del)*H(:,:,i)-eye(2))*L'*inv(G);
                    end

                    for j = 1:num
                        if (j~=i && adj(j,i))
                            C(:,:,j,i) = C_KCF(:,:,i);
                        end
                    end

                    K(:,:,i) = ((P(:,:,k,i,i) + C_KCF(:,:,i)*L)*H(:,:,i)')/(R(:,:,i) + H(:,:,i)*P(:,:,k,i,i)*H(:,:,i)');
                end    
                
                %%
                
                if Scheme == 'ICF'
                   
                    y_hat = zeros(2,1);
                    S_hat = zeros(2,2);
                    
                    Px_ICF = zeros(2,1);
                    P_ICF = zeros(2,2);
                    
                    for j = 1:num
                        if adj(i,j)
                            y_hat = y_hat + y_ICF(:,k,j);
                            S_hat = S_hat + S_ICF(:,:,j);
                            Px_ICF = Px_ICF + inv(P(:,:,k,j,j))*xbar(:,k,j);
                            P_ICF = P_ICF + inv(P(:,:,k,j,j));
                        end
                    end
                    
                    M(:,:,k,i,i) = inv(S_hat + (1/nnz(adj(:,i)))*P_ICF);
                    xhat(:,k,i) = M(:,:,k,i,i)*(y_hat + (1/nnz(adj(:,i)))*Px_ICF);
                    
                end
                
                 %%
                
                if Scheme == 'Olf'
                    
                    C_Olf = eps*P(:,:,k,i,i)/(1+norm(P(:,:,k,i,i),'fro'));
                    K(:,:,i) = (P(:,:,k,i,i)*H(:,:,i)')/(R(:,:,i) + H(:,:,i)*P(:,:,k,i,i)*H(:,:,i)');
                    for j = 1:num
                        if (j~=i && adj(j,i))
                            C(:,:,j,i) = C_Olf(:,:);
                        end
                    end
                    
                end    
               

                % F_i
                F(:,:,i) = eye(2) - K(:,:,i)*H(:,:,i);
            end

            for i=1:num

                sum1 = [0 0]';
                for j=1:num
                    if (i~=j && adj(i,j))
                        sum1 = sum1+ C(:,:,j,i)*(xbar(:,k,j)-xbar(:,k,i));
                    end
                end
                
                % ---------------- Estimates and Covariances ---------------- %

                for j=1:num

                    sum3 = zeros(2,2);
                    sum4 = zeros(2,2);
                    D(:,:,i,j) = zeros(2,2);

                    % P_rj-P_ij
                    for r = 1:num
                        if (i~=r && adj(r,i))
                            sum3 = sum3 + C(:,:,r,i)*(P(:,:,k,r,j)-P(:,:,k,i,j));
                        end
                    end
                    % P_is-P_ij
                    for s = 1:num
                        if (s~=j && adj(s,j))
                            sum4 = sum4 + (P(:,:,k,i,s)-P(:,:,k,i,j))*C(:,:,s,j)';
                        end
                    end
                    % D_ij
                    for r = 1:num
                        for s = 1:num
                            if (r~=i && s~=j && adj(r,i) && adj(s,j))
                                D(:,:,i,j) = D(:,:,i,j) + C(:,:,r,i)*(P(:,:,k,r,s)+P(:,:,k,i,j)-P(:,:,k,r,j)-P(:,:,k,i,s))*C(:,:,s,j)';
                            end
                        end
                    end

                    if Scheme == 'Raj' | Scheme == 'Inv' | Scheme == 'Olf'
                        xhat(:,k,i) = xbar(:,k,i) + K(:,:,i)*(z(:,k,i)-H(:,:,i)*xbar(:,k,i)) + sum1;

                        % Note the P_ij and M_ij should be updated irrespective of whether i and j are connected
                        if(i==j)
                            M(:,:,k,i,j) = F(:,:,i)*P(:,:,k,i,j)*F (:,:,j)' + sum3*F(:,:,j)' + F(:,:,i)*sum4 + D(:,:,i,j) + K(:,:,i)*R(:,:,i)*K (:,:,j)';
                        else
                            M(:,:,k,i,j) = F(:,:,i)*P(:,:,k,i,j)*F (:,:,j)' + sum3*F(:,:,j)' + F(:,:,i)*sum4 + D(:,:,i,j);
                        end
                    end

                    P(:,:,k+1,i,j) = A*M(:,:,k,i,j)*A' + B*Q*B';

                end
                    
                xbar(:,k+1,i) = A*xhat(:,k,i);
% 
%                 if norm(xhat(:,k,i)-x(:,k)) > 100
%                     error_norm = 1
%                     return
%                 end

                
            end
        end


        
        for t = 1:TIME
            RMSE3(MC,t) = 0.0;
            for s = 1:num
               RMSE3(MC,t) = RMSE3(MC,t) + norm(xhat(:,t,s) - x(:,t))   ; 
            end
        end
        
        if mod(MC,250)==0
            MC/num_MC*100
        end

    end
        % Plots
    %     fontname = 'Helvetica';
    %     set(0,'defaultaxesfontname',fontname);
    %     set(0,'defaulttextfontname',fontname);
    %     set(0,'defaulttextinterpreter','latex')
    %     plot(xhat(1,:,1),xhat(2,:,1),'ro-')
    %     hold on
    %     plot(x(1,:),x(2,:),'k')
    %     xlabel('x-position of target')
    %     ylabel('y-position of target')
    %     legend('Target estimate','Actual position')
%%
    clf

    if all(Scheme=='Raj')
       RMSE_Raj = RMSE3(:,:) ;
    end

    if all(Scheme=='Inv')
       RMSE_New = RMSE3(:,:) ;
    end
    
    if all(Scheme=='ICF')
       RMSE_ICF = RMSE3(:,:) ;
    end
    
    if all(Scheme=='Olf')
       RMSE_Olf = RMSE3(:,:) ;
    end

    if exist('RMSE_Olf','var')==1
       plot(mean(RMSE_Olf',2),'black--') ; 
       hold on;
    end
    
    if exist('RMSE_Raj','var')==1
       plot(mean(RMSE_Raj',2),'r--'); 
%        xlim([1 20])
%        ylim([0 15])
       hold on;
    end


    if exist('RMSE_New','var')==1
       plot(mean(RMSE_New',2),'b-') ;   
       hold on;
    end
    
    if exist('RMSE_ICF','var')==1
       plot(mean(RMSE_ICF',2),'g-') ;   
       hold on;
    end
    

    
legend('KCF', 'Optimal KCF', 'Optimal KCF 2019');
ylabel('Trace of Covariance');
xlabel('Iteration');
    %    plot(RMSE3(1,:))

end