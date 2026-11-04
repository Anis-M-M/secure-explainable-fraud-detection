package com.frauddetection.config;

import com.frauddetection.model.User;
import com.frauddetection.repository.UserRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * Creates the first admin account from environment variables, so no default
 * credentials are stored in the repository. Existing accounts are never changed.
 */
@Component
@Slf4j
public class AdminBootstrap implements ApplicationRunner {

    private static final int MIN_PASSWORD_LENGTH = 12;

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final String username;
    private final String email;
    private final String password;

    public AdminBootstrap(UserRepository userRepository,
                          PasswordEncoder passwordEncoder,
                          @Value("${app.admin.username}") String username,
                          @Value("${app.admin.email}") String email,
                          @Value("${app.admin.password:}") String password) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.username = username;
        this.email = email;
        this.password = password;
    }

    @Override
    public void run(ApplicationArguments args) {
        if (userRepository.existsByUsername(username) || userRepository.existsByEmail(email)) {
            return;
        }
        if (password.isBlank()) {
            log.warn("ADMIN_PASSWORD is not set, so no admin account was created");
            return;
        }
        if (password.length() < MIN_PASSWORD_LENGTH || password.startsWith("replace-with")) {
            throw new IllegalStateException(
                    "ADMIN_PASSWORD must be your own value of at least " + MIN_PASSWORD_LENGTH + " characters");
        }

        userRepository.save(User.builder()
                .username(username)
                .email(email)
                .passwordHash(passwordEncoder.encode(password))
                .firstName("System")
                .lastName("Admin")
                .role(User.Role.ADMIN)
                .isActive(true)
                .build());
        log.info("Created admin account: {}", username);
    }
}
